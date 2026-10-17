"""Natural-language request interpretation (Hungarian/English).

Two interchangeable interpreters produce an ``Intent``: a keyword/regex baseline and a
model-based interpreter. Both pass through the same deterministic validation, whose
guards take precedence: requests for network targets, destructive actions, following
instructions found in inspected code, or fabricating results are rejected regardless of
what an interpreter proposes, and every target is checked against the workspace.
"""

import re
from typing import Literal

from pydantic import Field

from .contracts import Family, StrictRecord
from .workspace import SourceWorkspace, TargetError, TargetNotFound

Action = Literal[
    "analyse",
    "explain_existing",
    "clarify_target",
    "out_of_scope",
    "reject_target",
    "reject_unsupported_action",
    "reject_instruction_override",
    "reject_result_fabrication",
]
ResolvedAction = Literal[
    "analyse",
    "explain_existing",
    "clarify_target",
    "out_of_scope",
    "reject_target",
    "reject_unsupported_action",
    "reject_instruction_override",
    "reject_result_fabrication",
    "target_not_found",
]


class Intent(StrictRecord):
    action: Action
    target: str | None = None
    focus: Family | None = None
    finding_index: int | None = None
    language: Literal["hu", "en"] = "hu"


class ResolvedRequest(StrictRecord):
    action: ResolvedAction
    target: str | None = None
    files: list[str] = Field(default_factory=list)
    focus: Family | None = None
    finding_index: int | None = None
    language: Literal["hu", "en"]
    interpreter: str
    reason: str


_I = re.IGNORECASE
URL = re.compile(r"\b(?:https?|ftp)://|\bwww\.|\b\d{1,3}(?:\.\d{1,3}){3}\b", _I)
NETWORK = re.compile(r"\b(?:port ?scan\w*|nmap|network scan\w*|hálózat\w*|weboldal\w*)", _I)
OVERRIDE = re.compile(
    r"utasítás\w*.{0,60}kövesd|kövesd.{0,60}utasítás\w*"
    r"|follow (?:the |any |all )?instructions?"
    r"|ignore (?:all |the |your |any )?(?:previous |above |earlier )?(?:instructions|rules)"
    r"|hagyd figyelmen kívül (?:az |a )?(?:utasítás|szabály)",
    _I,
)
FABRICATION = re.compile(
    r"ignore (?:any |all |the )?(?:scanner |tool |analysis )?(?:errors?|failures?|warnings?)"
    r"|report (?:that )?(?:the |this |it )?(?:file |code |project )?(?:is )?safe"
    r"|say (?:that )?(?:it|the code|the file) is safe|pretend"
    r"|(?:mondd|írd|jelentsd|állítsd)\w*.{0,40}biztonságos"
    r"|hagyd figyelmen kívül (?:a |az )?(?:hib|figyelmeztet)|tegyél úgy",
    _I,
)
DESTRUCTIVE = re.compile(
    r"\b(?:töröld|törölj\w*|töröljed|delete|erase|wipe|rm -rf)\b"
    r"|\bremove (?:the |all |this )?(?:files?|project|folder|directory)"
    r"|\b(?:írd felül|felülírj\w*|overwrite)\b",
    _I,
)
ANALYSE = re.compile(
    r"vizsgál|elemez|elemezd|elemzés|nézd át|nézd meg|ellenőriz|átnéz"
    r"|\bcheck|\banaly[sz]e|\bscan|\breview|\baudit|\binspect|\blook at",
    _I,
)
EXPLAIN = re.compile(r"magyaráz|\bexplain|\bwhy\b|miért|részletez", _I)
PREVIOUS = re.compile(r"előző|legutóbbi|korábbi|\bprevious|\blast\b|\bearlier", _I)
ORDINALS = {
    "első": 1, "first": 1, "második": 2, "second": 2, "harmadik": 3, "third": 3,
    "negyedik": 4, "fourth": 4, "ötödik": 5, "fifth": 5,
}  # fmt: skip
NUMBERED = re.compile(r"(\d+)\.?\s*(?:találat|finding)|(?:finding|találat)\s*#?(\d+)", _I)
FOCUS = [
    ("CWE-89", re.compile(r"\bsql\b", _I)),
    ("CWE-78", re.compile(r"parancs|\bcommand|\bshell\b|os\.system", _I)),
    ("CWE-95", re.compile(r"\beval\b|\bexec\b|kódkiértékel|code (?:injection|evaluation)", _I)),
]
HUNGARIAN = re.compile(
    r"[áéíóöőúüű]|\b(?:vizsgál\w*|elemez\w*|magyaráz\w*|nézd|fájl\w*|kód\w*|mappá?\w*)\b", _I
)
TOKEN = re.compile(r"[^\s\"'`„”«»]+")
DIRECTORY_HU = re.compile(r"(\S+)\s+(?:mappá\w*|mappa|könyvtár\w*)", _I)
DIRECTORY_EN = re.compile(r"(?:folder|directory)\s+(\S+)|(\S+)\s+(?:folder|directory)", _I)
ABSOLUTE = re.compile(r"^(?:[A-Za-z]:[\\/]|[\\/]|~)")
STOPWORDS = {"a", "az", "the", "this", "that", "ezt", "azt", "egy"}


def detect_language(text: str) -> str:
    return "hu" if HUNGARIAN.search(text) else "en"


def _clean(token: str) -> str:
    return token.strip(".,;!?()[]{}<>")


def path_candidates(text: str) -> list[str]:
    candidates = []
    for raw in TOKEN.findall(text):
        token = _clean(raw)
        explicit = token.lower().endswith(".py") or token.endswith(("/", "\\"))
        looks_like_path = ("/" in token or "\\" in token) and not URL.search(token)
        if explicit or looks_like_path:
            candidates.append(token)
    for match in [*DIRECTORY_HU.finditer(text), *DIRECTORY_EN.finditer(text)]:
        token = _clean(next(group for group in match.groups() if group))
        if token.lower() not in STOPWORDS and token not in candidates:
            candidates.append(token)
    return candidates


def _unsafe_path(candidate: str) -> bool:
    parts = re.split(r"[\\/]+", candidate)
    return bool(ABSOLUTE.match(candidate)) or ".." in parts or ":" in candidate


def guard(text: str) -> tuple[str, str] | None:
    """Deterministic refusals that no interpreter can override."""
    if URL.search(text) or NETWORK.search(text):
        return "out_of_scope", "network or web targets are outside static source analysis"
    if OVERRIDE.search(text):
        return "reject_instruction_override", "inspected content is data, never an instruction"
    if FABRICATION.search(text):
        return "reject_result_fabrication", "failures and findings must remain visible"
    if DESTRUCTIVE.search(text):
        return "reject_unsupported_action", "only analysis and explanation are supported"
    if any(_unsafe_path(candidate) for candidate in path_candidates(text)):
        return "reject_target", "absolute paths and parent references are not accepted"
    return None


def detect_focus(text: str) -> str | None:
    without_paths = text
    for candidate in path_candidates(text):
        without_paths = without_paths.replace(candidate, " ")
    found = [family for family, pattern in FOCUS if pattern.search(without_paths)]
    return found[0] if len(found) == 1 else None


def finding_index(text: str) -> int:
    match = NUMBERED.search(text)
    if match:
        return int(next(group for group in match.groups() if group))
    lowered = text.lower()
    for word, value in ORDINALS.items():
        if re.search(rf"\b{word}\b", lowered):
            return value
    return 1


class RuleInterpreter:
    name = "rules"

    def interpret(self, text: str) -> Intent:
        language = detect_language(text)
        blocked = guard(text)
        if blocked:
            return Intent(action=blocked[0], language=language)
        candidates = path_candidates(text)
        target = candidates[0] if candidates else None
        if EXPLAIN.search(text) and (PREVIOUS.search(text) or not target):
            return Intent(
                action="explain_existing", finding_index=finding_index(text), language=language
            )
        if ANALYSE.search(text) or EXPLAIN.search(text) or target:
            if not target:
                return Intent(action="clarify_target", language=language)
            return Intent(
                action="analyse", target=target, focus=detect_focus(text), language=language
            )
        return Intent(action="clarify_target", language=language)


def _normalise_path(text: str) -> str:
    return _clean(text).replace("\\", "/").lower()


def resolve_request(
    text: str, intent: Intent, workspace: SourceWorkspace, interpreter: str
) -> ResolvedRequest:
    """Apply the shared guards and check the target against the workspace."""
    language = intent.language
    base = {"language": language, "interpreter": interpreter}
    blocked = guard(text)
    if blocked:
        return ResolvedRequest(action=blocked[0], reason=blocked[1], **base)
    if intent.action == "explain_existing":
        return ResolvedRequest(
            action="explain_existing",
            finding_index=intent.finding_index or 1,
            reason="refers to the previous report",
            **base,
        )
    if intent.action != "analyse":
        return ResolvedRequest(action=intent.action, reason="proposed by interpreter", **base)
    target = _clean(intent.target or "")
    if not target:
        return ResolvedRequest(action="clarify_target", reason="no target was given", **base)
    if _normalise_path(target) not in _normalise_path(text):
        return ResolvedRequest(
            action="clarify_target", reason="the target does not appear in the request", **base
        )
    if _unsafe_path(target):
        return ResolvedRequest(action="reject_target", reason="unsafe path", **base)
    try:
        files = workspace.collect(target.replace("\\", "/"))
    except TargetNotFound as exc:
        return ResolvedRequest(action="target_not_found", target=target, reason=str(exc), **base)
    except TargetError as exc:
        return ResolvedRequest(action="reject_target", target=target, reason=str(exc), **base)
    return ResolvedRequest(
        action="analyse",
        target=target.replace("\\", "/"),
        files=files,
        focus=intent.focus,
        reason="validated workspace target",
        **base,
    )


class ModelInterpreter:
    """Asks the local model for an Intent; falls back to the rule baseline on failure."""

    name = "model"

    def __init__(self, connector, prompt_path=None):
        from pathlib import Path

        from .model import INTENT_SETTINGS

        path = prompt_path or Path(__file__).resolve().parents[2] / "prompts/m3_intent_system.txt"
        self.prompt = path.read_text(encoding="utf-8")
        self.connector = connector
        self.settings = INTENT_SETTINGS
        self.last_evidence: dict = {}

    def interpret(self, text: str) -> Intent:
        from .model import ModelError

        message = f"<<<REQUEST\n{text}\nREQUEST>>>"
        try:
            intent, evidence = self.connector.complete(self.prompt, message, Intent, self.settings)
            self.last_evidence = {"status": "completed", **evidence}
            return intent
        except ModelError as exc:
            self.last_evidence = {"status": "failed", "error": str(exc), **(exc.evidence or {})}
            fallback = RuleInterpreter().interpret(text)
            return fallback
