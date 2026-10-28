"""Invoke the installed analyzers; never execute the fixture source code."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("tool", ["bandit", "semgrep"])
@pytest.mark.parametrize(
    "fixture,expected",
    [
        ("unsafe_eval.py", 1),
        ("literal_only.py", 0),
        ("text_only.py", 0),
    ],
)
def test_scanner_installation(tool, fixture, expected, output_dir):
    target = f"tests/fixtures/{fixture}"
    if tool == "bandit":
        command = [sys.executable, "-m", "bandit", "-t", "B307", "-f", "json", target]
    else:
        executable = Path(sys.executable).parent / ("semgrep.exe" if os.name == "nt" else "semgrep")
        command = [
            str(executable),
            "scan",
            "--config",
            "semgrep/smoke_eval.yml",
            "--metrics=off",
            "--disable-version-check",
            "--no-git-ignore",
            "--strict",
            "--error",
            "--json",
            target,
        ]
    environment = os.environ.copy()
    environment.update(
        {
            "SEMGREP_SEND_METRICS": "off",
            "SEMGREP_ENABLE_VERSION_CHECK": "0",
            "PYTHONUTF8": "1",
        }
    )
    stem = output_dir / f"{tool}-{Path(fixture).stem}"
    started = time.perf_counter()
    process = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )
    stem.with_suffix(".stdout.json").write_text(process.stdout, encoding="utf-8")
    stem.with_suffix(".stderr.txt").write_text(process.stderr, encoding="utf-8")
    record = {
        "command": command,
        "cwd": str(ROOT),
        "exit_code": process.returncode,
        "seconds": round(time.perf_counter() - started, 3),
        "expected_findings": expected,
        "check_passed": False,
    }
    try:
        assert process.returncode == expected, process.stderr
        report = json.loads(process.stdout)
        assert not report.get("errors"), report.get("errors")
        assert len(report["results"]) == expected
        # A zero-result run must actually have scanned the target.
        if tool == "semgrep":
            assert len(report["paths"]["scanned"]) == 1
        else:
            assert report["metrics"]["_totals"]["loc"] > 0
        if expected:
            finding = report["results"][0]
            if tool == "bandit":
                assert finding["test_id"] == "B307"
                assert finding["line_number"] == 2
            else:
                assert finding["check_id"].endswith("smoke-python-eval")
                assert finding["start"]["line"] == 2
        record["actual_findings"] = len(report["results"])
        record["check_passed"] = True
    finally:
        stem.with_suffix(".check.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
