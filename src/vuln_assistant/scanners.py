"""Local scanner adapters. Their rule sets remain separate from model output."""

import ast
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from .contracts import Finding, ScanReport
from .workspace import SourceWorkspace

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class LocalScanner:
    def __init__(self, tool: str, workspace: SourceWorkspace, timeout: float = 30):
        if tool not in {"bandit", "semgrep"}:
            raise ValueError("Unsupported scanner")
        self.tool = tool
        self.workspace = workspace
        self.timeout = timeout

    def scan(self, relative_path: str) -> ScanReport:
        target = self.workspace.resolve(relative_path)
        relative = target.relative_to(self.workspace.root).as_posix()
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        report = ScanReport(tool=self.tool, status="failed", target=relative, source_sha256=digest)
        if self.tool == "bandit":
            command = [
                sys.executable,
                "-m",
                "bandit",
                "-t",
                "B307,B602,B608",
                "--ignore-nosec",
                "-f",
                "json",
                str(target),
            ]
        else:
            executable = Path(sys.executable).parent / (
                "semgrep.exe" if os.name == "nt" else "semgrep"
            )
            command = [
                str(executable),
                "scan",
                "--config",
                str(PROJECT_ROOT / "rules/m2_python.yml"),
                "--metrics=off",
                "--disable-version-check",
                "--no-git-ignore",
                "--disable-nosem",
                "--strict",
                "--error",
                "--json",
                str(target),
            ]
        env = os.environ.copy()
        env.update(SEMGREP_SEND_METRICS="off", SEMGREP_ENABLE_VERSION_CHECK="0", PYTHONUTF8="1")
        report.execution = {"command": command, "cwd": str(self.workspace.root)}
        started = time.perf_counter()
        try:
            # Some scanner parsers recover from malformed input without an error.
            # Establish Python 3.11 syntax validity before trusting a zero-finding result.
            ast.parse(target.read_bytes(), filename=relative)
            process = subprocess.run(
                command,
                cwd=self.workspace.root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self.timeout,
                check=False,
            )
            report.execution.update(
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
            )
            if process.returncode not in {0, 1}:
                raise ValueError(f"Scanner failed with exit code {process.returncode}")
            raw = json.loads(process.stdout)
            if not isinstance(raw, dict):
                raise TypeError("Scanner response must be a JSON object")
            if raw.get("errors"):
                raise ValueError(f"Scanner reported errors: {raw['errors']}")
            if self.tool == "bandit":
                scanned = [p for p in raw["metrics"] if p != "_totals"]
            else:
                scanned = raw["paths"]["scanned"]
            if not any(self._same_target(p, target) for p in scanned):
                raise ValueError("Scanner did not report scanning the requested file")
            if (process.returncode == 1) != bool(raw["results"]):
                raise ValueError("Scanner exit code disagrees with its findings")
            for item in raw["results"]:
                if self.tool == "bandit":
                    path, rule, line = item["filename"], item["test_id"], item["line_number"]
                    cwe = item.get("issue_cwe", {}).get("id")
                    fields = {
                        "severity": item["issue_severity"],
                        "confidence": item["issue_confidence"],
                        "message": item["issue_text"],
                        "cwe": f"CWE-{cwe}" if cwe else None,
                    }
                else:
                    path, rule, line = item["path"], item["check_id"], item["start"]["line"]
                    fields = {
                        "severity": item["extra"]["severity"],
                        "message": item["extra"]["message"],
                        "cwe": item["extra"].get("metadata", {}).get("cwe"),
                    }
                if not self._same_target(path, target):
                    raise ValueError("Scanner returned a finding outside the requested file")
                identity = f"{self.tool}:{rule}:{relative}:{line}:{digest}"
                report.findings.append(
                    Finding(
                        id=hashlib.sha256(identity.encode()).hexdigest()[:24],
                        tool=self.tool,
                        rule_id=rule,
                        path=relative,
                        line=line,
                        **fields,
                    )
                )
            # Detect common accidental edits during the diagnostic. This is not an OS sandbox.
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError("Source changed during analysis; discard this result")
            report.scanned_files = [relative]
            report.status = "completed"
        except (
            OSError,
            subprocess.TimeoutExpired,
            ValueError,
            KeyError,
            TypeError,
            SyntaxError,
        ) as exc:
            report.findings = []
            report.errors = [str(exc)]
        finally:
            report.execution["seconds"] = round(time.perf_counter() - started, 3)
        return report

    def _same_target(self, reported: str, target: Path) -> bool:
        path = Path(reported)
        if not path.is_absolute():
            path = self.workspace.root / path
        return path.resolve() == target
