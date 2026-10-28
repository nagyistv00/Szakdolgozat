"""Scan the development samples with the basic scanner setup.

With --with-model it also checks that the local model reads scanner output correctly.
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

from vulnscan.handshake import check_connection
from vulnscan.model import OllamaConnector
from vulnscan.scanners import LocalScanner
from vulnscan.workspace import SourceWorkspace

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-model", action="store_true")
    args = parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H%M%S")
    output = ROOT / "results" / "sample_scans" / stamp
    output.mkdir(parents=True)
    print(f"Output: {output}", flush=True)
    manifest = json.loads((ROOT / "data/samples/manifest.json").read_text(encoding="utf-8"))
    hashes = {}
    for folder in ("src", "semgrep", "prompts", "data/samples", "scripts", "tests"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
    for name in ("uv.lock", "pyproject.toml", ".python-version"):
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "packages": dict(
            sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())
        ),
        "input_sha256": hashes,
        "purpose": "Sample scans with the basic scanner setup; not an accuracy evaluation",
    }
    (output / "manifest.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    workspace = SourceWorkspace(ROOT / "data/samples")
    summary = {"scans": [], "model_requested": args.with_model, "model_checked": False}
    handshake_report = None
    for tool in ("bandit", "semgrep"):
        scanner = LocalScanner(tool, workspace)
        for case in manifest["cases"]:
            path = workspace.resolve(case["path"])
            if hashlib.sha256(path.read_bytes()).hexdigest() != case["sha256"]:
                raise RuntimeError(f"Sample file changed: {case['id']}")
            report = scanner.scan(case["path"])
            (output / f"{tool}-{case['id']}.json").write_text(
                report.model_dump_json(indent=2), encoding="utf-8"
            )
            summary["scans"].append(
                {
                    "tool": tool,
                    "case": case["id"],
                    "status": report.status,
                    "finding_count": len(report.findings),
                    "errors": report.errors,
                }
            )
            if tool == "bandit" and case["id"] == "eval_direct_bad":
                handshake_report = report
        print(f"{tool}: all samples scanned", flush=True)
    try:
        if any(item["status"] != "completed" for item in summary["scans"]):
            raise RuntimeError("One or more scans failed; see the JSON files in the output folder")
        if args.with_model:
            model = OllamaConnector()
            metadata = model.metadata()
            (output / "model-metadata.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )
            prompt = (ROOT / "prompts/handshake.txt").read_text(encoding="utf-8")
            if handshake_report is None or not handshake_report.findings:
                raise RuntimeError("Expected a finding for the model handshake")
            result = check_connection(handshake_report, model, prompt)
            (output / "model-connection.json").write_text(
                json.dumps(result, indent=2), encoding="utf-8"
            )
            summary["model_checked"] = True
            print("The local model read the scanner output correctly", flush=True)
    except Exception as exc:
        summary["failure"] = str(exc)
        if getattr(exc, "evidence", None):
            (output / "model-failure.json").write_text(
                json.dumps(exc.evidence, indent=2), encoding="utf-8"
            )
        raise
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Sample scans finished.")


if __name__ == "__main__":
    main()
