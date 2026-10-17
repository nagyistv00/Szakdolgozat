import hashlib
import json
import subprocess
from pathlib import Path

import httpx
import pytest

from vuln_assistant.contracts import ConnectionAck, Finding, ScanReport
from vuln_assistant.diagnostic import check_connection
from vuln_assistant.model import ModelError, OllamaConnector
from vuln_assistant.scanners import LocalScanner
from vuln_assistant.workspace import SourceWorkspace, TargetError

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path", ["../outside.py", "C:\\outside.py", "/outside.py", "file.py:stream", "missing.py", ""]
)
def test_workspace_rejects_invalid_targets(tmp_path, path):
    with pytest.raises(TargetError):
        SourceWorkspace(tmp_path).resolve(path)


def test_workspace_checks_type_size_and_spaces(tmp_path):
    (tmp_path / "source file.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "other.txt").write_text("pass\n", encoding="utf-8")
    workspace = SourceWorkspace(tmp_path)
    assert workspace.resolve("source file.py") == tmp_path / "source file.py"
    with pytest.raises(TargetError):
        workspace.resolve("other.txt")
    with pytest.raises(TargetError):
        SourceWorkspace(tmp_path, max_bytes=2).resolve("source file.py")


@pytest.mark.parametrize("tool", ["bandit", "semgrep"])
@pytest.mark.parametrize(
    "source,expected_status,expected_count",
    [
        ("def f(x):\n    return eval(x)\n", "completed", 1),
        ("def f(x):\n    return int(x)\n", "completed", 0),
        ("def broken(:\n", "failed", 0),
    ],
)
def test_real_scanner_adapter(tool, source, expected_status, expected_count, tmp_path):
    path = tmp_path / "source file.py"
    path.write_text(source, encoding="utf-8")
    report = LocalScanner(tool, SourceWorkspace(tmp_path)).scan(path.name)
    assert report.status == expected_status, report.errors
    assert len(report.findings) == expected_count
    assert report.source_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    if expected_status == "completed":
        assert report.scanned_files == [path.name]
        assert not report.errors
    else:
        assert report.errors


@pytest.mark.parametrize("fault", ["timeout", "exit", "json", "skipped", "foreign", "changed"])
def test_scanner_failures_are_not_clean_results(monkeypatch, tmp_path, fault):
    path = tmp_path / "source.py"
    path.write_text("pass\n", encoding="utf-8")

    def run(command, **kwargs):
        if fault == "timeout":
            raise subprocess.TimeoutExpired(command, 0.01)
        if fault == "changed":
            path.write_text("pass\n# changed\n", encoding="utf-8")
        result = {"errors": [], "results": [], "paths": {"scanned": [str(path)]}}
        if fault == "skipped":
            result["paths"]["scanned"] = []
        if fault == "foreign":
            result["results"] = [
                {
                    "path": "../outside.py",
                    "check_id": "r",
                    "start": {"line": 1},
                    "extra": {"severity": "WARNING", "message": "x"},
                }
            ]
        code = 2 if fault == "exit" else (1 if fault == "foreign" else 0)
        return subprocess.CompletedProcess(
            command, code, "[]" if fault == "json" else json.dumps(result), ""
        )

    monkeypatch.setattr("vuln_assistant.scanners.subprocess.run", run)
    report = LocalScanner("semgrep", SourceWorkspace(tmp_path)).scan(path.name)
    assert report.status == "failed"
    assert report.errors
    assert not report.findings


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://localhost:11435",
        "http://127.0.0.1:11435/remote",
        "http://user:pass@127.0.0.1:11435",
    ],
)
def test_model_cannot_send_data_to_external_or_ambiguous_endpoint(url):
    with pytest.raises(ValueError):
        OllamaConnector(base_url=url)


def make_response(content, **changes):
    response = {"done": True, "done_reason": "stop", "message": {"content": json.dumps(content)}}
    response.update(changes)
    return response


def test_model_schema_request_and_validation():
    def handle(request):
        data = json.loads(request.content)
        assert request.url.path == "/api/chat"
        assert data["stream"] is False and data["format"]["additionalProperties"] is False
        assert data["options"]["seed"] == 0 and "tools" not in data
        return httpx.Response(
            200, json=make_response({"received_finding_ids": ["a"], "source_tool": "bandit"})
        )

    model = OllamaConnector(transport=httpx.MockTransport(handle))
    reply, _ = model.complete("system", "input", ConnectionAck)
    assert reply.received_finding_ids == ["a"]


@pytest.mark.parametrize(
    "fault", ["timeout", "http", "redirect", "not_json", "bad_schema", "truncated", "tool_call"]
)
def test_model_errors_are_explicit(fault):
    def handle(request):
        if fault == "timeout":
            raise httpx.ReadTimeout("test timeout", request=request)
        if fault == "http":
            return httpx.Response(500, json={"error": "unavailable"})
        if fault == "redirect":
            return httpx.Response(302, headers={"location": "https://example.com"})
        if fault == "not_json":
            return httpx.Response(200, text="not json")
        body = make_response({"received_finding_ids": ["a"], "source_tool": "bandit"})
        if fault == "bad_schema":
            body["message"]["content"] = '{"received_finding_ids": 1, "source_tool": "bandit"}'
        if fault == "truncated":
            body["done_reason"] = "length"
        if fault == "tool_call":
            body["message"]["tool_calls"] = [{"function": {"name": "execute"}}]
        return httpx.Response(200, json=body)

    with pytest.raises(ModelError):
        OllamaConnector(transport=httpx.MockTransport(handle)).complete("s", "u", ConnectionAck)


def test_handshake_rejects_invented_evidence_and_failed_scans():
    report = ScanReport(
        tool="bandit",
        status="completed",
        target="a.py",
        source_sha256="abc",
        findings=[
            Finding(
                id="real",
                tool="bandit",
                rule_id="B307",
                path="a.py",
                line=1,
                severity="MEDIUM",
                message="potential eval",
            )
        ],
    )
    model = OllamaConnector(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json=make_response({"received_finding_ids": ["invented"], "source_tool": "bandit"}),
            )
        )
    )
    with pytest.raises(ModelError):
        check_connection(report, model, "acknowledge")
    report.status = "failed"
    with pytest.raises(ValueError):
        check_connection(report, model, "acknowledge")


def test_missing_model_is_explicit():
    model = OllamaConnector(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"version": "test"} if request.url.path == "/api/version" else {"models": []},
            )
        )
    )
    with pytest.raises(ModelError, match="not installed"):
        model.metadata()


def test_corpus_integrity_and_grouping():
    root = ROOT / "data/m2"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    assert len(cases) == len({c["id"] for c in cases}) == 18
    assert {c["cwe"] for c in cases} == {"CWE-95", "CWE-78", "CWE-89"}
    assert sum(c["expected_vulnerable"] for c in cases) == 6
    for case in cases:
        assert case["rationale"]
        path = SourceWorkspace(root).resolve(case["path"])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == case["sha256"]
        if case["expected_vulnerable"]:
            assert any(
                other["group"] == case["group"] and not other["expected_vulnerable"]
                for other in cases
            )
