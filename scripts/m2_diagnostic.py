"""Run connectors on development fixtures and optionally verify the real local model."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

from vuln_assistant.diagnostic import check_connection
from vuln_assistant.model import OllamaConnector
from vuln_assistant.scanners import LocalScanner
from vuln_assistant.workspace import SourceWorkspace

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-model", action="store_true")
    args = parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "artifacts/m2" / stamp
    output.mkdir(parents=True)
    print(f"Evidence: {output}", flush=True)
    manifest = json.loads((ROOT / "data/m2/manifest.json").read_text(encoding="utf-8"))
    hashes = {}
    for folder in ("src", "rules", "prompts", "data/m2", "scripts", "tests"):
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
        "purpose": "Connector diagnostics on development fixtures, not final accuracy evaluation",
    }
    (output / "manifest.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    workspace = SourceWorkspace(ROOT / "data/m2")
    summary = {"scans": [], "model_requested": args.with_model, "model_checked": False}
    handshake_report = None
    for tool in ("bandit", "semgrep"):
        scanner = LocalScanner(tool, workspace)
        for case in manifest["cases"]:
            path = workspace.resolve(case["path"])
            if hashlib.sha256(path.read_bytes()).hexdigest() != case["sha256"]:
                raise RuntimeError(f"Corpus hash changed: {case['id']}")
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
        print(f"Completed {tool} connector checks", flush=True)
    try:
        if any(item["status"] != "completed" for item in summary["scans"]):
            raise RuntimeError("One or more connector scans failed; inspect their evidence")
        if args.with_model:
            model = OllamaConnector()
            metadata = model.metadata()
            (output / "model-metadata.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )
            prompt = (ROOT / "prompts/connection_ack.txt").read_text(encoding="utf-8")
            if handshake_report is None or not handshake_report.findings:
                raise RuntimeError("Expected a finding for the connector handshake")
            result = check_connection(handshake_report, model, prompt)
            (output / "model-connection.json").write_text(
                json.dumps(result, indent=2), encoding="utf-8"
            )
            summary["model_checked"] = True
            print("Real local model acknowledged scanner evidence correctly", flush=True)
    except Exception as exc:
        summary["failure"] = str(exc)
        if getattr(exc, "evidence", None):
            (output / "model-failure.json").write_text(
                json.dumps(exc.evidence, indent=2), encoding="utf-8"
            )
        raise
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Connector diagnostic complete; no detection-accuracy claim.")


if __name__ == "__main__":
    main()
