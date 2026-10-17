"""Explicit download only; normal connector calls never fetch models.

    uv run --locked python scripts/pull_model.py --model qwen2.5-coder:14b

An installed model is not downloaded again. Identity (digest, size, licence) is recorded
under artifacts/m3/ (the milestone 2 record stays in artifacts/m2/model-install.json).
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    args = parser.parse_args()
    with httpx.Client(base_url="http://127.0.0.1:11435", timeout=600, trust_env=False) as client:
        tags = client.get("/api/tags")
        tags.raise_for_status()
        installed = {m["name"] for m in tags.json()["models"]}
        if args.model in installed:
            print(f"{args.model} is already installed; no download.", flush=True)
        else:
            with client.stream("POST", "/api/pull", json={"model": args.model}) as response:
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
        info = client.post("/api/show", json={"model": args.model})
        info.raise_for_status()
        tags = client.get("/api/tags")
        tags.raise_for_status()
        runtime = client.get("/api/version")
        runtime.raise_for_status()
    selected = next(m for m in tags.json()["models"] if m["name"] == args.model)
    record = {
        "captured_utc": datetime.now(UTC).isoformat(),
        "runtime": runtime.json(),
        "model": selected,
        "show": info.json(),
    }
    safe = args.model.replace(":", "_").replace("/", "_")
    destination = ROOT / "artifacts/m3" / f"model-install-{safe}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"{args.model} digest {selected.get('digest')} recorded: {destination}")


if __name__ == "__main__":
    main()
