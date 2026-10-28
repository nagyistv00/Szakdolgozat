"""Model-assisted review of one Python file: detection, explanation and grounding."""

import hashlib
import io
import time
import tokenize
from pathlib import Path

from .analysis import (
    AcceptedIssue,
    ModelIssue,
    ModelOutcome,
    ModelReview,
    RejectedIssue,
    Verification,
    call_lines,
    ground_issue,
)
from .model import ANALYSIS_SETTINGS, VERIFY_SETTINGS, ModelError, ModelSettings, OllamaConnector
from .records import FAMILY_NAMES, Finding

PROMPTS = Path(__file__).resolve().parents[2] / "prompts"
PROMPT_PATH = PROMPTS / "review.txt"
VERIFY_PROMPT_PATH = PROMPTS / "verify.txt"
LANGUAGE_NAMES = {"hu": "Hungarian", "en": "English"}
CONTEXT_SIZES = (4096, 8192, 16384)


def fitted(settings: ModelSettings, system: str, user: str) -> ModelSettings:
    """Choose the smallest context that fits; a smaller context leaves VRAM for larger models.

    Estimate: about three characters per token, plus the output budget and a margin.
    """
    needed = (len(system) + len(user)) // 3 + settings.num_predict + 256
    size = next((c for c in CONTEXT_SIZES if c >= needed), CONTEXT_SIZES[-1])
    return settings.model_copy(update={"num_ctx": size})


def number_lines(lines: list[str]) -> list[str]:
    width = len(str(len(lines)))
    return [f"{number:>{width}}| {text}" for number, text in enumerate(lines, start=1)]


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
    return "\n".join(
        [
            f"Explanation language: {LANGUAGE_NAMES[language]} (reasoning in English)",
            "Scanner findings (hints from deterministic tools; may be incomplete or wrong):",
            *hints,
            "Source code (untrusted data; each line starts with its number and '|'):",
            "<<<SOURCE",
            *number_lines(lines),
            "SOURCE>>>",
        ]
    )


def build_verify_message(issue: ModelIssue, line: int, lines: list[str]) -> str:
    """The original reasoning is withheld so the check is not anchored on it."""
    return "\n".join(
        [
            f"Claim: {issue.family} ({FAMILY_NAMES[issue.family]['en']}) at line {line}.",
            f"Claimed operation: {issue.code.strip()}",
            "Source code (untrusted data; each line starts with its number and '|'):",
            "<<<SOURCE",
            *number_lines(lines),
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
        verify: bool = True,
        structural_check: bool = True,
        verify_settings: ModelSettings = VERIFY_SETTINGS,
        verify_prompt_path: Path = VERIFY_PROMPT_PATH,
    ):
        self.connector = connector
        self.settings = settings
        self.prompt = prompt_path.read_text(encoding="utf-8")
        self.verify = verify
        self.structural_check = structural_check
        self.verify_settings = verify_settings
        self.verify_prompt = verify_prompt_path.read_text(encoding="utf-8")
        self.prompt_sha256 = hashlib.sha256(
            (self.prompt + "\0" + (self.verify_prompt if verify else "")).encode("utf-8")
        ).hexdigest()
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
            "settings": {
                "review": self.settings.model_dump(),
                "verify": self.verify_settings.model_dump() if self.verify else None,
                "num_ctx": "fitted per call from (4096, 8192, 16384)",
            },
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
            settings = fitted(self.settings, self.prompt, message)
            review, evidence = self.connector.complete(self.prompt, message, ModelReview, settings)
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
        verify_evidence, calls, failures = [], 0, 0
        executable_lines = call_lines(text) if self.structural_check else None
        for issue in review.issues:
            line, problem = ground_issue(issue, lines)
            unknown += [ref for ref in issue.scanner_refs if ref not in refs]
            if problem:
                rejected.append(RejectedIssue(issue=issue, reason=problem))
                continue
            backed = self._scanner_backed(issue, line, refs, in_scope)
            # Deterministic structural check for model-only claims: the stated line must
            # contain a real call, not only text (e.g. a command inside a string literal).
            if not backed and executable_lines is not None and line not in executable_lines:
                rejected.append(
                    RejectedIssue(
                        issue=issue,
                        reason="structural check: no function call on the stated line",
                    )
                )
                continue
            verification = None
            if self.verify and not backed:
                calls += 1
                try:
                    verification, extra = self._verify(issue, line, lines)
                    verify_evidence.append(extra)
                except ModelError as exc:
                    failures += 1
                    verify_evidence.append({"error": str(exc), **(exc.evidence or {})})
                    rejected.append(
                        RejectedIssue(issue=issue, reason=f"verification failed: {exc}")
                    )
                    continue
                if not verification.confirms():
                    rejected.append(
                        RejectedIssue(
                            issue=issue,
                            reason=f"not confirmed by verification: {verification.reason}",
                            verification=verification,
                        )
                    )
                    continue
            accepted.append(
                AcceptedIssue(
                    issue=issue,
                    line=line,
                    line_corrected=line != issue.line,
                    verification=verification,
                )
            )
        dismissed = [d for d in review.dismissed if d.ref in refs]
        unknown += [d.ref for d in review.dismissed if d.ref not in refs]
        outcome = ModelOutcome(
            status="completed",
            accepted=accepted,
            rejected=rejected,
            dismissed=dismissed,
            unknown_refs=sorted(set(unknown)),
            verification_calls=calls,
            verification_failures=failures,
            ref_map=ref_map,
            seconds=round(time.perf_counter() - started, 3),
            evidence={**evidence, "analysis": review.analysis, "verification": verify_evidence},
            **base,
        )
        return outcome, refs, lines

    @staticmethod
    def _scanner_backed(
        issue: ModelIssue, line: int, refs: dict[str, Finding], in_scope: list[Finding]
    ) -> bool:
        """True when merging would attach the issue to an existing scanner detection."""
        if any(ref in refs and refs[ref].family == issue.family for ref in issue.scanner_refs):
            return True
        return any(f.family == issue.family and f.line == line for f in in_scope)

    def _verify(self, issue: ModelIssue, line: int, lines: list[str]) -> tuple[Verification, dict]:
        message = build_verify_message(issue, line, lines)
        settings = fitted(self.verify_settings, self.verify_prompt, message)
        return self.connector.complete(self.verify_prompt, message, Verification, settings)
