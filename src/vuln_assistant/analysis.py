"""Milestone 3 records, model-claim grounding and the scanner/model merge.

Pure logic without network or subprocess access, so it can be tested in isolation.

Merge policy (supervisor priority: detection > explanation > NL control > false-positive
recognition): scanner findings are never removed by the model. A model issue that is
grounded in the source either confirms/explains a scanner finding or is added as a new
detection. Ungrounded model claims are kept in the evidence but never become detections.
"""

import re
from typing import Literal

from pydantic import Field

from .contracts import Family, Finding, ScanReport, StrictRecord


class ModelIssue(StrictRecord):
    """One vulnerability claimed by the model. Field order puts reasoning first."""

    reasoning: str
    family: Family
    line: int
    code: str
    input_source: str
    scanner_refs: list[str]
    explanation: str
    fix: str


class DismissedFinding(StrictRecord):
    ref: str
    reason: str


class ModelReview(StrictRecord):
    analysis: str
    issues: list[ModelIssue]
    dismissed: list[DismissedFinding]


class Verification(StrictRecord):
    """Second, focused check of a model-only claim. Questions come before the verdict."""

    trace: str
    attacker_controlled: bool
    reaches_dangerous_operation: bool
    neutralised: bool
    verdict: Literal["vulnerable", "not_vulnerable"]
    reason: str

    def confirms(self) -> bool:
        """Confirmed only when the verdict and every answer agree."""
        return (
            self.verdict == "vulnerable"
            and self.attacker_controlled
            and self.reaches_dangerous_operation
            and not self.neutralised
        )


class AcceptedIssue(StrictRecord):
    issue: ModelIssue
    line: int
    line_corrected: bool
    # None: backed by a scanner finding, so no verification call was needed.
    verification: Verification | None = None


class RejectedIssue(StrictRecord):
    issue: ModelIssue
    reason: str
    verification: Verification | None = None


class ModelOutcome(StrictRecord):
    status: Literal["completed", "failed", "skipped"]
    reason: str | None = None
    model: str | None = None
    model_digest: str | None = None
    prompt_sha256: str | None = None
    settings: dict = Field(default_factory=dict)
    accepted: list[AcceptedIssue] = Field(default_factory=list)
    rejected: list[RejectedIssue] = Field(default_factory=list)
    dismissed: list[DismissedFinding] = Field(default_factory=list)
    unknown_refs: list[str] = Field(default_factory=list)
    verification_calls: int = 0
    verification_failures: int = 0
    ref_map: dict[str, str] = Field(default_factory=dict)
    seconds: float | None = None
    evidence: dict = Field(default_factory=dict)


class Detection(StrictRecord):
    family: Family
    path: str
    line: int
    code_line: str
    detected_by: list[str]
    finding_ids: list[str]
    scanner_messages: list[str]
    explanation_source: Literal["model", "scanner"]
    explanation: str | None = None
    fix: str | None = None
    input_source: str | None = None


class FileAnalysis(StrictRecord):
    path: str
    source_sha256: str
    scans: list[ScanReport]
    model: ModelOutcome
    detections: list[Detection]


class AnalysisReport(StrictRecord):
    created_utc: str
    target: str
    language: Literal["hu", "en"]
    mode: Literal["scanners", "scanners+model"]
    focus: Family | None = None
    files: list[FileAnalysis]
    complete: bool
    problems: list[str]
    hidden_other_families: int = 0
    summary: str = ""


_LINE_PREFIX = re.compile(r"^\s*\d+\s*\|\s?")


def _normalise(text: str) -> str:
    return " ".join(text.split())


def ground_issue(issue: ModelIssue, lines: list[str]) -> tuple[int | None, str | None]:
    """Check that the model quoted real code at (or within two lines of) the stated line.

    Returns (line, None) when grounded, possibly with a corrected line number, or
    (None, reason) when the claim cannot be tied to the source.
    """
    quote = _normalise(_LINE_PREFIX.sub("", issue.code.strip()))
    if len(quote) < 3:
        return None, "quoted code is empty or too short"
    if "\n" in issue.code.strip():
        return None, "quoted code spans several lines"
    normalised = [_normalise(line) for line in lines]
    if 1 <= issue.line <= len(lines) and quote in normalised[issue.line - 1]:
        return issue.line, None
    nearby = [
        number
        for number in range(max(1, issue.line - 2), min(len(lines), issue.line + 2) + 1)
        if quote in normalised[number - 1]
    ]
    if len(nearby) == 1:
        return nearby[0], None
    return None, "quoted code was not found at or near the stated line"


def merge(
    path: str,
    lines: list[str],
    scans: list[ScanReport],
    outcome: ModelOutcome,
    findings_by_ref: dict[str, Finding],
) -> list[Detection]:
    """Combine in-scope scanner findings with grounded model issues for one file."""
    groups: dict[tuple[str, int], dict] = {}

    def group(family: str, line: int) -> dict:
        key = (family, line)
        if key not in groups:
            groups[key] = {
                "family": family,
                "line": line,
                "tools": [],
                "ids": [],
                "messages": [],
                "model": None,
            }
        return groups[key]

    for report in scans:
        if report.status != "completed":
            continue
        for finding in report.findings:
            if finding.family is None:
                continue
            entry = group(finding.family, finding.line)
            if finding.tool not in entry["tools"]:
                entry["tools"].append(finding.tool)
            entry["ids"].append(finding.id)
            entry["messages"].append(f"{finding.tool} {finding.rule_id}: {finding.message}")

    for accepted in outcome.accepted:
        issue = accepted.issue
        keys = {
            (findings_by_ref[ref].family, findings_by_ref[ref].line)
            for ref in issue.scanner_refs
            if ref in findings_by_ref and findings_by_ref[ref].family == issue.family
        }
        if not keys:
            keys = {(issue.family, accepted.line)}
        for family, line in sorted(keys):
            entry = group(family, line)
            if "model" not in entry["tools"]:
                entry["tools"].append("model")
            if entry["model"] is None:
                entry["model"] = issue

    detections = []
    for (family, line), entry in sorted(groups.items(), key=lambda item: (item[0][1], item[0][0])):
        issue: ModelIssue | None = entry["model"]
        detections.append(
            Detection(
                family=family,
                path=path,
                line=line,
                code_line=lines[line - 1].strip() if 1 <= line <= len(lines) else "",
                detected_by=entry["tools"],
                finding_ids=entry["ids"],
                scanner_messages=entry["messages"],
                explanation_source="model" if issue else "scanner",
                explanation=issue.explanation if issue else None,
                fix=issue.fix if issue else None,
                input_source=issue.input_source if issue else None,
            )
        )
    return detections
