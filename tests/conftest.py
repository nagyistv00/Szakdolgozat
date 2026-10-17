"""Preserve installation-check evidence independently of conversation history."""

import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def evidence_dir():
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    directory = ROOT / "artifacts" / "m1" / stamp
    directory.mkdir(parents=True, exist_ok=False)
    paths = [ROOT / "uv.lock", ROOT / "pyproject.toml", ROOT / ".python-version"]
    for folder in ("tests", "rules"):
        paths.extend(
            path
            for path in (ROOT / folder).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
    manifest = {
        "started_utc": stamp,
        "purpose": "Installation smoke checks, not vulnerability accuracy evaluation",
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": dict(
            sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())
        ),
        "input_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in sorted(set(paths))
        },
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nEvidence directory: {directory}")
    return directory
