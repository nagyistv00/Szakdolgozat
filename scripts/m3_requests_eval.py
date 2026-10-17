"""Milestone 3 request-interpretation run on the 12 development scenarios.

The rule interpreter was written with these scenarios in view, so its score is a
development observation. Held-out paraphrases are needed for the M4 evaluation.
"""

import argparse
import json
import time

from vuln_assistant.evidence import ROOT, environment_manifest, run_directory, write_json
from vuln_assistant.intent import ModelInterpreter, RuleInterpreter, resolve_request
from vuln_assistant.model import DEFAULT_MODEL, OllamaConnector
from vuln_assistant.workspace import SourceWorkspace


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--models", default=DEFAULT_MODEL, help="comma-separated Ollama tags")
    parser.add_argument("--out")
    args = parser.parse_args()
    out = run_directory("artifacts/m3", "requests", args.out)
    write_json(
        out / "manifest.json",
        environment_manifest("M3 request scenarios (development)", {"args": vars(args)}),
    )
    corpus = ROOT / "data/m2"
    scenarios = json.loads((corpus / "requests.json").read_text(encoding="utf-8"))["cases"]
    workspace = SourceWorkspace(corpus)
    interpreters = [RuleInterpreter()]
    if not args.no_model:
        for model in [m.strip() for m in args.models.split(",") if m.strip()]:
            interpreter = ModelInterpreter(OllamaConnector(model=model))
            interpreter.name = f"model:{model}"
            interpreters.append(interpreter)
    results, summary = [], {}
    for interpreter in interpreters:
        passed = action_correct = failures = 0
        for case in scenarios:
            started = time.perf_counter()
            intent = interpreter.interpret(case["text"])
            seconds = round(time.perf_counter() - started, 3)
            evidence = getattr(interpreter, "last_evidence", {})
            failed = evidence.get("status") == "failed"
            failures += failed
            request = resolve_request(case["text"], intent, workspace, interpreter.name)
            checks = {
                "action": request.action == case["expected"],
                "language": request.language == case["language"],
                "focus": request.focus == case.get("focus"),
                "target": "target" not in case or request.target == case["target"],
            }
            action_correct += checks["action"]
            passed += all(checks.values())
            results.append(
                {
                    "interpreter": interpreter.name,
                    "id": case["id"],
                    "expected": case["expected"],
                    "raw_intent": intent.model_dump(),
                    "resolved": request.model_dump(),
                    "checks": checks,
                    "model_failed": failed,
                    "seconds": seconds,
                    "model_reply": evidence.get("response", {}).get("message", {}).get("content")
                    if evidence
                    else None,
                }
            )
        summary[interpreter.name] = {
            "scenarios": len(scenarios),
            "action_correct": action_correct,
            "all_checks_passed": passed,
            "model_failures": failures,
        }
        print(f"{interpreter.name}: {summary[interpreter.name]}", flush=True)
    write_json(out / "results.json", {"summary": summary, "results": results})


if __name__ == "__main__":
    main()
