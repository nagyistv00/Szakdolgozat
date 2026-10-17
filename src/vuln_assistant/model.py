"""Loopback-only, schema-validated Ollama connector; no tool execution."""

from typing import TypeVar
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "qwen2.5-coder:7b"
# Digest recorded at milestone 2 (artifacts/m2/model-install.json).
KNOWN_DIGESTS = {
    "qwen2.5-coder:7b": "dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364",
}


class ModelError(RuntimeError):
    def __init__(self, message: str, evidence: dict | None = None):
        super().__init__(message)
        self.evidence = evidence


class ModelSettings(BaseModel):
    """Generation settings; recorded with every call so runs can be compared."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    temperature: float = 0
    seed: int = 0
    num_ctx: int = 4096
    num_predict: int = 256
    # Seconds (or an Ollama duration string) to keep the model loaded after the call.
    # 0 unloads immediately: right for a single diagnostic, wasteful for a batch.
    keep_alive: int | str = 0


HANDSHAKE_SETTINGS = ModelSettings()
ANALYSIS_SETTINGS = ModelSettings(num_ctx=8192, num_predict=2048, keep_alive="10m")
VERIFY_SETTINGS = ModelSettings(num_ctx=8192, num_predict=768, keep_alive="10m")
INTENT_SETTINGS = ModelSettings(num_ctx=2048, num_predict=256, keep_alive="10m")


class OllamaConnector:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = "http://127.0.0.1:11435",
        timeout: float = 300,
        transport: httpx.BaseTransport | None = None,
    ):
        parsed = urlparse(base_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "::1"}
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            raise ValueError("The current connector requires an explicit loopback HTTP endpoint")
        if not model or "cloud" in model.lower():
            raise ValueError("Select an installed local model")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            trust_env=False,
            follow_redirects=False,
            transport=self.transport,
        )

    def metadata(self, expected_digest: str | None = None) -> dict:
        """Read runtime/model identity. With ``expected_digest`` a moved tag is an error."""
        try:
            with self._client() as client:
                version = client.get("/api/version")
                version.raise_for_status()
                tags = client.get("/api/tags")
                tags.raise_for_status()
            models = tags.json()["models"]
            selected = next((m for m in models if m["name"] == self.model), None)
            if selected is None:
                raise ModelError("The selected model is not installed; no automatic download")
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise ModelError(f"Cannot read local model metadata: {exc}") from exc
        if expected_digest and selected.get("digest") != expected_digest:
            raise ModelError(
                f"Model digest {selected.get('digest')} differs from the recorded {expected_digest}"
            )
        return {"runtime": version.json(), "model": selected}

    def complete(
        self,
        system: str,
        user: str,
        schema: type[T],
        settings: ModelSettings = HANDSHAKE_SETTINGS,
    ) -> tuple[T, dict]:
        request = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "format": schema.model_json_schema(),
            "stream": False,
            "options": {
                "temperature": settings.temperature,
                "seed": settings.seed,
                "num_ctx": settings.num_ctx,
                "num_predict": settings.num_predict,
            },
            "keep_alive": settings.keep_alive,
        }
        evidence = {"request": request}
        try:
            with self._client() as client:
                response = client.post("/api/chat", json=request)
                evidence["http_status"] = response.status_code
                evidence["response_text"] = response.text
                response.raise_for_status()
            raw = response.json()
            evidence["response"] = raw
            if not isinstance(raw, dict) or not isinstance(raw.get("message"), dict):
                raise ModelError("Model response must contain a message object", evidence)
            if raw.get("done") is not True or raw.get("done_reason") != "stop":
                raise ModelError("Model output is incomplete or generation hit its limit", evidence)
            if raw["message"].get("tool_calls"):
                raise ModelError("Unexpected tool call in a data-only connector", evidence)
            result = schema.model_validate_json(raw["message"]["content"])
            return result, evidence
        except (httpx.HTTPError, ValueError, KeyError, TypeError, ValidationError) as exc:
            raise ModelError(f"Invalid local model response: {exc}", evidence) from exc

    def unload(self) -> None:
        """Ask the server to release the model after a batch (best effort)."""
        try:
            with self._client() as client:
                client.post("/api/generate", json={"model": self.model, "keep_alive": 0})
        except httpx.HTTPError:
            pass
