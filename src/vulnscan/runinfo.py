"""Run folders and environment manifests shared by the evaluation scripts."""

import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKED = ("src", "semgrep", "prompts", "data", "scripts", "tests")
RESULTS = ROOT / "results"


def run_directory(name: str, explicit: str | None = None) -> Path:
    """results/<UTC date>_<time>_<name>, unless an explicit folder is given."""
    if explicit:
        path = Path(explicit)
    else:
        stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H%M%S")
        path = RESULTS / f"{stamp}_{name}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def environment_manifest(purpose: str, extra: dict | None = None) -> dict:
    hashes = {}
    for folder in TRACKED:
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
    for name in ("uv.lock", "pyproject.toml", ".python-version"):
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    return {
        "created_utc": datetime.now(UTC).isoformat(),
        "purpose": purpose,
        "python": sys.version,
        "platform": platform.platform(),
        "argv": sys.argv,
        "packages": dict(
            sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())
        ),
        "input_sha256": hashes,
        **(extra or {}),
    }


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
