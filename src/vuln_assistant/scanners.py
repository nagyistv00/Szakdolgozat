"""Local scanner adapters. Their rule sets remain separate from model output.

Each adapter runs a fixed command without a shell, validates that the requested file was
really analysed, and returns an immutable, source-linked report. A failed or partial scan
is reported as ``failed``; it is never turned into an empty, successful result.
"""

import ast
import hashlib
import json
import os
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path

from .contracts import Finding, ScanReport
from .workspace import SourceWorkspace

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Bandit checks whose documented purpose is the scoped injection pattern itself.
# Bandit's own CWE field is preserved separately: it reports CWE-78 for eval (B307),
# so per-family evaluation must not rely on it. Informational checks such as B404
# (subprocess import), B603/B606 (no shell) and B607 (partial path) are deliberately
# outside the families: they flag APIs, not an injection flow.
BANDIT_FAMILY = {
    "B102": "CWE-95",  # exec used
    "B307": "CWE-95",  # eval (blacklist call)
    "B601": "CWE-78",  # paramiko exec_command
    "B602": "CWE-78",  # subprocess call with shell=True
    "B604": "CWE-78",  # any other function with shell=True
    "B605": "CWE-78",  # start process with a shell (os.system, os.popen, ...)
    "B609": "CWE-78",  # wildcard injection
    "B608": "CWE-89",  # SQL built from strings
    "B610": "CWE-89",  # Django extra()
    "B611": "CWE-89",  # Django RawSQL
}

# Fixed, versioned scanner configurations. "m2" reproduces the milestone 2 diagnostics;
# "m3" is the baseline used from milestone 3 on (full Bandit, taint-mode Semgrep rules).
PROFILES = {
    "m2": {
        "bandit": {"tests": ("B307", "B602", "B608")},
        "semgrep": {"config": "rules/m2_python.yml"},
    },
    "m3": {
        "bandit": {"tests": None},
        "semgrep": {"config": "rules/m3_python_taint.yml"},
    },
}


def normalise_semgrep_rule(check_id: str) -> str:
    """Semgrep prefixes rule IDs with the dotted config path (including the user's
    home directory). Project rule IDs contain no dots, so the last segment is the ID."""
    return check_id.rsplit(".", 1)[-1]


class SubprocessScanner(ABC):
    tool: str

    def __init__(self, workspace: SourceWorkspace, profile: str, timeout: float = 60):
        self.workspace = workspace
        self.profile = profile
        self.timeout = timeout

    @abstractmethod
    def command(self, target: Path) -> list[str]: ...

    @abstractmethod
    def scanned_paths(self, raw: dict) -> list[str]: ...

    @abstractmethod
    def parse(self, item: dict) -> tuple[str, str, int, dict]:
        """Return reported path, normalised rule ID, line and remaining Finding fields."""

    def scan(self, relative_path: str) -> ScanReport:
        target = self.workspace.resolve(relative_path)
        relative = target.relative_to(self.workspace.root).as_posix()
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        report = ScanReport(
            tool=self.tool,
            status="failed",
            target=relative,
            source_sha256=digest,
            profile=self.profile,
        )
        command = self.command(target)
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
            if not any(self._same_target(p, target) for p in self.scanned_paths(raw)):
                raise ValueError("Scanner did not report scanning the requested file")
            if (process.returncode == 1) != bool(raw["results"]):
                raise ValueError("Scanner exit code disagrees with its findings")
            for item in raw["results"]:
                path, rule, line, fields = self.parse(item)
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
            # Detect common accidental edits during the analysis. This is not an OS sandbox.
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


class BanditScanner(SubprocessScanner):
    tool = "bandit"

    def __init__(
        self,
        workspace: SourceWorkspace,
        profile: str = "m3",
        tests: tuple[str, ...] | None = None,
        timeout: float = 60,
    ):
        super().__init__(workspace, profile, timeout)
        self.tests = tests

    def command(self, target: Path) -> list[str]:
        command = [sys.executable, "-m", "bandit"]
        if self.tests:
            command += ["-t", ",".join(self.tests)]
        return command + ["--ignore-nosec", "-f", "json", str(target)]

    def scanned_paths(self, raw: dict) -> list[str]:
        return [p for p in raw["metrics"] if p != "_totals"]

    def parse(self, item: dict) -> tuple[str, str, int, dict]:
        rule = item["test_id"]
        cwe = (item.get("issue_cwe") or {}).get("id")
        return (
            item["filename"],
            rule,
            item["line_number"],
            {
                "severity": item["issue_severity"],
                "confidence": item["issue_confidence"],
                "message": item["issue_text"],
                "cwe": f"CWE-{cwe}" if cwe else None,
                "family": BANDIT_FAMILY.get(rule),
            },
        )


class SemgrepScanner(SubprocessScanner):
    tool = "semgrep"

    def __init__(
        self,
        workspace: SourceWorkspace,
        profile: str = "m3",
        config: str = "rules/m3_python_taint.yml",
        timeout: float = 60,
    ):
        super().__init__(workspace, profile, timeout)
        self.config = PROJECT_ROOT / config

    def command(self, target: Path) -> list[str]:
        executable = Path(sys.executable).parent / ("semgrep.exe" if os.name == "nt" else "semgrep")
        return [
            str(executable),
            "scan",
            "--config",
            str(self.config),
            "--metrics=off",
            "--disable-version-check",
            "--no-git-ignore",
            "--disable-nosem",
            "--strict",
            "--error",
            "--json",
            str(target),
        ]

    def scanned_paths(self, raw: dict) -> list[str]:
        return raw["paths"]["scanned"]

    def parse(self, item: dict) -> tuple[str, str, int, dict]:
        metadata = item["extra"].get("metadata", {})
        cwe = metadata.get("cwe")
        return (
            item["path"],
            normalise_semgrep_rule(item["check_id"]),
            item["start"]["line"],
            {
                "severity": item["extra"]["severity"],
                "message": item["extra"]["message"],
                "cwe": cwe,
                # Only project rules are configured; their metadata states the family.
                "family": cwe if cwe in {"CWE-95", "CWE-78", "CWE-89"} else None,
            },
        )


def make_scanner(
    tool: str, workspace: SourceWorkspace, profile: str = "m3", timeout: float = 60
) -> SubprocessScanner:
    if profile not in PROFILES:
        raise ValueError("Unknown scanner profile")
    if tool == "bandit":
        return BanditScanner(workspace, profile, timeout=timeout, **PROFILES[profile]["bandit"])
    if tool == "semgrep":
        return SemgrepScanner(workspace, profile, timeout=timeout, **PROFILES[profile]["semgrep"])
    raise ValueError("Unsupported scanner")


def LocalScanner(tool: str, workspace: SourceWorkspace, timeout: float = 30) -> SubprocessScanner:
    """Milestone 2 entry point, kept so the M2 diagnostic and its tests reproduce unchanged."""
    return make_scanner(tool, workspace, profile="m2", timeout=timeout)
