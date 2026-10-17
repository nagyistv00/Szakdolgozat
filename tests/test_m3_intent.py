"""Request interpretation, shared guards and the command-line flow."""

import json
from pathlib import Path

import httpx
import pytest

from vuln_assistant.cli import main
from vuln_assistant.intent import Intent, ModelInterpreter, RuleInterpreter, resolve_request
from vuln_assistant.metrics import evaluate
from vuln_assistant.model import OllamaConnector
from vuln_assistant.workspace import SourceWorkspace

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/m2"
SCENARIOS = json.loads((CORPUS / "requests.json").read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", SCENARIOS, ids=[c["id"] for c in SCENARIOS])
def test_rule_interpreter_on_development_scenarios(case):
    """Development scenarios: the rules were written with these in view."""
    intent = RuleInterpreter().interpret(case["text"])
    request = resolve_request(case["text"], intent, SourceWorkspace(CORPUS), "rules")
    assert request.action == case["expected"]
    assert request.language == case["language"]
    assert request.focus == case.get("focus")
    if "target" in case:
        assert request.target == case["target"]


def model_connector(intent: dict | None):
    def handle(request):
        if intent is None:
            return httpx.Response(500, json={"error": "down"})
        body = {"done": True, "done_reason": "stop", "message": {"content": json.dumps(intent)}}
        return httpx.Response(200, json=body)

    return OllamaConnector(transport=httpx.MockTransport(handle))


@pytest.mark.parametrize(
    "text,proposed,expected",
    [
        (
            "Nézd meg a cases/eval_direct_bad.py fájlt",
            {"action": "analyse", "target": "cases/eval_direct_bad.py", "language": "hu"},
            "analyse",
        ),
        (
            "Nézd át a kódot",
            {"action": "analyse", "target": "cases/eval_direct_bad.py", "language": "hu"},
            "clarify_target",
        ),
        (
            "Scan https://example.com/cases/eval_direct_bad.py",
            {"action": "analyse", "target": "cases/eval_direct_bad.py", "language": "en"},
            "out_of_scope",
        ),
        (
            "Analyse ../../secret.py",
            {"action": "analyse", "target": "../../secret.py", "language": "en"},
            "reject_target",
        ),
        (
            "Check cases/none.py",
            {"action": "analyse", "target": "cases/none.py", "language": "en"},
            "target_not_found",
        ),
    ],
)
def test_guards_and_workspace_checks_override_model(text, proposed, expected):
    interpreter = ModelInterpreter(model_connector(proposed))
    intent = interpreter.interpret(text)
    request = resolve_request(text, intent, SourceWorkspace(CORPUS), "model")
    assert request.action == expected


def test_language_and_focus_are_not_taken_from_the_model():
    """Observed in the first target run: wrong language, and a filter taken from a file name."""
    text = "Check cases/sql_integer_control.py, and show the source line behind each warning."
    proposed = Intent(
        action="analyse", target="cases/sql_integer_control.py", focus="CWE-89", language="hu"
    )
    request = resolve_request(text, proposed, SourceWorkspace(CORPUS), "model")
    assert request.language == "en" and request.focus is None
    text = "Nézd meg a cases/sql_direct_bad.py fájlt adatbázis-lekérdezések szempontjából."
    proposed = Intent(action="analyse", target="cases/sql_direct_bad.py", focus="CWE-89")
    request = resolve_request(text, proposed, SourceWorkspace(CORPUS), "model")
    assert request.language == "hu" and request.focus == "CWE-89"


def test_model_interpreter_falls_back_to_rules_on_failure():
    interpreter = ModelInterpreter(model_connector(None))
    intent = interpreter.interpret("Check cases/sql_direct_bad.py for SQL injection.")
    assert interpreter.last_evidence["status"] == "failed"
    assert intent.action == "analyse" and intent.focus == "CWE-89"


def test_cli_rejects_and_explains_without_previous_report(tmp_path, capsys):
    state = tmp_path / "state.json"
    common = ["--root", str(CORPUS), "--no-model", "--state", str(state)]
    assert main(["ask", "Vizsgáld meg a cases/missing.py fájlt.", *common]) == 4
    assert "nem található" in capsys.readouterr().out
    assert main(["ask", "Magyarázd el az előző elemzés első találatát.", *common]) == 4
    assert "Nincs korábbi elemzés" in capsys.readouterr().out


def test_cli_analyse_then_explain_with_real_scanners(tmp_path, capsys):
    state = tmp_path / "state.json"
    common = ["--root", str(CORPUS), "--no-model", "--state", str(state)]
    assert main(["ask", "Check cases/sql_direct_bad.py for SQL injection.", *common]) == 0
    output = capsys.readouterr().out
    assert "CWE-89" in output and state.exists()
    assert main(["ask", "Explain the first finding of the previous analysis.", *common]) == 0
    assert "sql_direct_bad.py" in capsys.readouterr().out


def test_metrics_keep_counts_and_undefined_ratios():
    result = evaluate([True, True, False, False], [True, False, True, False])
    assert result == {
        "tp": 1, "fp": 1, "tn": 1, "fn": 1, "n": 4,
        "accuracy": 0.5, "precision": 0.5, "recall": 0.5,
    }  # fmt: skip
    assert evaluate([False], [False])["precision"] is None
    with pytest.raises(ValueError):
        evaluate([True], [])
