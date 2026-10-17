"""Tool-neutral data exchanged by independently replaceable components."""

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


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
    cwe: str | None = None
    message: str


class ScanReport(StrictRecord):
    tool: str
    status: Literal["completed", "failed"]
    target: str
    source_sha256: str
    findings: list[Finding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    scanned_files: list[str] = Field(default_factory=list)
    execution: dict = Field(default_factory=dict)


class ConnectionAck(StrictRecord):
    """Connector handshake only; deliberately makes no vulnerability judgement."""

    received_finding_ids: list[str]
    source_tool: str


class Scanner(Protocol):
    def scan(self, relative_path: str) -> ScanReport: ...
