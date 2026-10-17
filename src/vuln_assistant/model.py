"""Loopback-only, schema-validated Ollama connector; no tool execution."""

from typing import TypeVar
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ModelError(RuntimeError):
    def __init__(self, message: str, evidence: dict | None = None):
        super().__init__(message)
        self.evidence = evidence


class OllamaConnector:
    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        base_url: str = "http://127.0.0.1:11435",
        timeout: float = 120,
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

    def metadata(self) -> dict:
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
            return {"runtime": version.json(), "model": selected}
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise ModelError(f"Cannot read local model metadata: {exc}") from exc

    def complete(self, system: str, user: str, schema: type[T]) -> tuple[T, dict]:
        request = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "format": schema.model_json_schema(),
            "stream": False,
            "options": {"temperature": 0, "seed": 0, "num_ctx": 4096, "num_predict": 256},
            "keep_alive": 0,
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
