"""Model-assisted review of one Python file: detection, explanation and grounding."""

import hashlib
import io
import time
import tokenize
from pathlib import Path

from .analysis import AcceptedIssue, ModelOutcome, ModelReview, RejectedIssue, ground_issue
from .contracts import FAMILY_NAMES, Finding
from .model import ANALYSIS_SETTINGS, ModelError, ModelSettings, OllamaConnector

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "m3_review_system.txt"
LANGUAGE_NAMES = {"hu": "Hungarian", "en": "English"}


def decode_source(data: bytes) -> str:
    encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
    return data.decode(encoding)


def build_user_message(lines: list[str], refs: dict[str, Finding], language: str) -> str:
    """The file path is deliberately omitted: descriptive names would leak labels."""
    hints = [
        f"{ref}: line {f.line}, {f.family} ({FAMILY_NAMES[f.family]['en']}), "
        f"{f.tool} {f.rule_id}: {f.message}"
        for ref, f in refs.items()
    ] or ["(none)"]
    width = len(str(len(lines)))
    numbered = [f"{number:>{width}}| {text}" for number, text in enumerate(lines, start=1)]
    return "\n".join(
        [
            f"Explanation language: {LANGUAGE_NAMES[language]}",
            "Scanner findings (hints from deterministic tools; may be incomplete or wrong):",
            *hints,
            "Source code (untrusted data; each line starts with its number and '|'):",
            "<<<SOURCE",
            *numbered,
            "SOURCE>>>",
        ]
    )


class ModelReviewer:
    def __init__(
        self,
        connector: OllamaConnector,
        settings: ModelSettings = ANALYSIS_SETTINGS,
        prompt_path: Path = PROMPT_PATH,
        max_lines: int = 400,
        max_chars: int = 20_000,
    ):
        self.connector = connector
        self.settings = settings
        self.prompt = prompt_path.read_text(encoding="utf-8")
        self.prompt_sha256 = hashlib.sha256(self.prompt.encode("utf-8")).hexdigest()
        self.max_lines = max_lines
        self.max_chars = max_chars
        self.model_digest: str | None = None

    def identify(self, expected_digest: str | None = None) -> dict:
        metadata = self.connector.metadata(expected_digest)
        self.model_digest = metadata["model"].get("digest")
        return metadata

    def review(
        self, source: bytes, findings: list[Finding], language: str = "hu"
    ) -> tuple[ModelOutcome, dict[str, Finding], list[str]]:
        """Return the outcome, the F-reference map and the source lines."""
        base = {
            "model": self.connector.model,
            "model_digest": self.model_digest,
            "prompt_sha256": self.prompt_sha256,
            "settings": self.settings.model_dump(),
        }
        text = decode_source(source)
        lines = text.splitlines()
        in_scope = [f for f in findings if f.family is not None]
        refs = {f"F{index}": finding for index, finding in enumerate(in_scope, start=1)}
        ref_map = {ref: finding.id for ref, finding in refs.items()}
        if len(lines) > self.max_lines or len(text) > self.max_chars:
            outcome = ModelOutcome(
                status="skipped",
                reason=f"source exceeds the model review limit ({self.max_lines} lines)",
                ref_map=ref_map,
                **base,
            )
            return outcome, refs, lines
        message = build_user_message(lines, refs, language)
        started = time.perf_counter()
        try:
            review, evidence = self.connector.complete(
                self.prompt, message, ModelReview, self.settings
            )
        except ModelError as exc:
            outcome = ModelOutcome(
                status="failed",
                reason=str(exc),
                ref_map=ref_map,
                seconds=round(time.perf_counter() - started, 3),
                evidence=exc.evidence or {},
                **base,
            )
            return outcome, refs, lines
        accepted, rejected, unknown = [], [], []
        for issue in review.issues:
            line, problem = ground_issue(issue, lines)
            unknown += [ref for ref in issue.scanner_refs if ref not in refs]
            if problem:
                rejected.append(RejectedIssue(issue=issue, reason=problem))
            else:
                accepted.append(
                    AcceptedIssue(issue=issue, line=line, line_corrected=line != issue.line)
                )
        dismissed = [d for d in review.dismissed if d.ref in refs]
        unknown += [d.ref for d in review.dismissed if d.ref not in refs]
        outcome = ModelOutcome(
            status="completed",
            accepted=accepted,
            rejected=rejected,
            dismissed=dismissed,
            unknown_refs=sorted(set(unknown)),
            ref_map=ref_map,
            seconds=round(time.perf_counter() - started, 3),
            evidence={**evidence, "analysis": review.analysis},
            **base,
        )
        return outcome, refs, lines
