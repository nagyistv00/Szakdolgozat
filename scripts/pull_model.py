"""Explicit download only; normal connector calls never fetch models."""

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]

with httpx.Client(base_url="http://127.0.0.1:11435", timeout=600, trust_env=False) as client:
    with client.stream("POST", "/api/pull", json={"model": "qwen2.5-coder:7b"}) as response:
        response.raise_for_status()
        last_status = None
        for line in response.iter_lines():
            if not line:
                continue
            item = json.loads(line)
            if "error" in item:
                raise RuntimeError(item["error"])
            status = item.get("status")
            if status != last_status:
                print(status, flush=True)
                last_status = status
        if last_status != "success":
            raise RuntimeError("Download did not complete successfully")
    info = client.post("/api/show", json={"model": "qwen2.5-coder:7b"})
    info.raise_for_status()
    tags = client.get("/api/tags")
    tags.raise_for_status()
    runtime = client.get("/api/version")
    runtime.raise_for_status()
record = {
    "captured_utc": datetime.now(UTC).isoformat(),
    "runtime": runtime.json(),
    "tags": tags.json(),
    "show": info.json(),
}
destination = ROOT / "artifacts/m2/model-install.json"
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(record, indent=2), encoding="utf-8")
print(f"Model metadata and digest recorded: {destination}")
