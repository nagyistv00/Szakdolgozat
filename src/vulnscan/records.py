"""Data records shared by the scanners, the model and the report."""

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

# The three weakness families the tool looks for.
Family = Literal["CWE-95", "CWE-78", "CWE-89"]
FAMILIES: tuple[str, ...] = ("CWE-95", "CWE-78", "CWE-89")
FAMILY_NAMES = {
    "CWE-95": {"en": "eval injection", "hu": "veszélyes dinamikus kódkiértékelés"},
    "CWE-78": {"en": "OS command injection", "hu": "parancsbefecskendezés"},
    "CWE-89": {"en": "SQL injection", "hu": "SQL-befecskendezés"},
}


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Finding(StrictRecord):
    id: str
    tool: str
    rule_id: str
    path: str
    line: int = Field(ge=1)
    severity: str
    confidence: str | None = None
    # CWE exactly as reported by the tool; Bandit, for example, reports CWE-78 for eval (B307).
    cwe: str | None = None
    # Project family assigned by our own rule map; None means outside the evaluated scope.
    family: Family | None = None
    message: str


class ScanReport(StrictRecord):
    tool: str
    status: Literal["completed", "failed"]
    target: str
    source_sha256: str
    profile: str | None = None
    findings: list[Finding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    scanned_files: list[str] = Field(default_factory=list)
    execution: dict = Field(default_factory=dict)


class ConnectionAck(StrictRecord):
    """Connector handshake only; deliberately makes no vulnerability judgement."""

    received_finding_ids: list[str]
    source_tool: str


class Scanner(Protocol):
    tool: str

    def scan(self, relative_path: str) -> ScanReport: ...
