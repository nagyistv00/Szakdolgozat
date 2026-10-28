"""One scanner-to-model connection check, with no user-command interpretation."""

import json

from .model import ModelError, OllamaConnector
from .records import ConnectionAck, ScanReport


def check_connection(report: ScanReport, model: OllamaConnector, prompt: str) -> dict:
    if report.status != "completed" or report.errors:
        raise ValueError("A failed scan must not be sent as a successful analysis")
    # No source code or corpus labels are needed for a connector handshake.
    payload = {"tool": report.tool, "findings": [f.model_dump() for f in report.findings]}
    reply, evidence = model.complete(prompt, json.dumps(payload), ConnectionAck)
    evidence["validated_reply"] = reply.model_dump()
    evidence["connection_valid"] = (
        reply.received_finding_ids == [f.id for f in report.findings]
        and reply.source_tool == report.tool
    )
    if not evidence["connection_valid"]:
        raise ModelError(
            "Model acknowledgement does not match the supplied scanner evidence", evidence
        )
    return evidence
