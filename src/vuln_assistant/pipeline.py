"""Orchestrates scanners and the optional model reviewer over a validated target."""

import hashlib
from datetime import UTC, datetime

from .analysis import AnalysisReport, FileAnalysis, ModelOutcome, merge
from .contracts import Family
from .report import render_summary
from .review import ModelReviewer, decode_source
from .scanners import SubprocessScanner
from .workspace import SourceWorkspace


class Analyzer:
    def __init__(
        self,
        workspace: SourceWorkspace,
        scanners: list[SubprocessScanner],
        reviewer: ModelReviewer | None = None,
        language: str = "hu",
    ):
        if language not in {"hu", "en"}:
            raise ValueError("Unsupported language")
        self.workspace = workspace
        self.scanners = scanners
        self.reviewer = reviewer
        self.language = language

    def analyse_file(self, relative: str) -> tuple[FileAnalysis, list[str]]:
        problems: list[str] = []
        path = self.workspace.resolve(relative)
        source = path.read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        scans = [scanner.scan(relative) for scanner in self.scanners]
        for scan in scans:
            if scan.status != "completed":
                problems.append(f"{relative}: {scan.tool} failed: {'; '.join(scan.errors)}")
            elif scan.source_sha256 != digest:
                problems.append(f"{relative}: source changed between analysis steps")
        findings = [f for scan in scans if scan.status == "completed" for f in scan.findings]
        if self.reviewer is None:
            outcome = ModelOutcome(status="skipped", reason="model review not requested")
            lines = decode_source(source).splitlines()
            refs = {}
        else:
            outcome, refs, lines = self.reviewer.review(source, findings, self.language)
            if outcome.status != "completed":
                problems.append(f"{relative}: model review {outcome.status}: {outcome.reason}")
            if outcome.verification_failures:
                problems.append(
                    f"{relative}: {outcome.verification_failures} model claim(s) could not be "
                    "verified and were not reported"
                )
        detections = merge(relative, lines, scans, outcome, refs)
        analysis = FileAnalysis(
            path=relative,
            source_sha256=digest,
            scans=scans,
            model=outcome,
            detections=detections,
        )
        return analysis, problems

    def analyse(self, target: str, focus: Family | None = None) -> AnalysisReport:
        files = self.workspace.collect(target)
        analyses, problems = [], []
        for relative in files:
            analysis, file_problems = self.analyse_file(relative)
            analyses.append(analysis)
            problems += file_problems
        hidden = 0
        if focus:
            hidden = sum(1 for a in analyses for d in a.detections if d.family != focus)
        report = AnalysisReport(
            created_utc=datetime.now(UTC).isoformat(),
            target=target,
            language=self.language,
            mode="scanners+model" if self.reviewer else "scanners",
            focus=focus,
            files=analyses,
            complete=not problems,
            problems=problems,
            hidden_other_families=hidden,
        )
        report.summary = render_summary(report)
        return report
