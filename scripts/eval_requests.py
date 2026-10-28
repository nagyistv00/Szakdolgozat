"""Evaluate the request interpreters on a labelled set of requests.

    data/requests_test.json  14 requests written independently of the interpreters
                             (default; workspace: data/lab)
    data/requests_dev.json   the 12 scenarios used during development
                             (use --cases data/requests_dev.json --root data/samples)

Scoring rules (fixed before the first run on the test set):
- action: resolved action equals the label;
- language: detected language equals the label;
- focus: resolved family filter equals the label (None when the label has no focus);
- target: compared only when the label is ``analyse`` or ``target_not_found`` — rejected
  or clarified requests carry no validated target by design;
- finding_index: compared only for ``explain_existing``.
A request passes when every applicable check holds.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

from vulnscan.intent import ModelInterpreter, RuleInterpreter, resolve_request
from vulnscan.model import DEFAULT_MODEL, OllamaConnector
from vulnscan.runinfo import ROOT, environment_manifest, run_directory, write_json
from vulnscan.workspace import SourceWorkspace

TARGET_CHECKED = {"analyse", "target_not_found"}


def check_case(case: dict, request) -> dict:
    checks = {
        "action": request.action == case["expected"],
        "language": request.language == case["language"],
        "focus": request.focus == case.get("focus"),
    }
    if case["expected"] in TARGET_CHECKED and "target" in case:
        checks["target"] = (request.target or "").rstrip("/") == case["target"].rstrip("/")
    if case["expected"] == "explain_existing" and "finding_index" in case:
        checks["finding_index"] = request.finding_index == case["finding_index"]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--cases", default=str(ROOT / "data/requests_test.json"))
    parser.add_argument("--root", default=str(ROOT / "data/lab"))
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--models", default=DEFAULT_MODEL, help="comma-separated Ollama tags")
    parser.add_argument("--out")
    args = parser.parse_args()
    cases_path = Path(args.cases).resolve()
    raw = cases_path.read_bytes()
    loaded = json.loads(raw.decode("utf-8"))
    cases = loaded["cases"] if isinstance(loaded, dict) else loaded
    out = run_directory("requests_eval", args.out)
    print(f"Output: {out}", flush=True)
    write_json(
        out / "manifest.json",
        environment_manifest(
            f"Request interpretation on {cases_path.name}",
            {
                "args": vars(args),
                "cases_sha256": hashlib.sha256(raw).hexdigest(),
                "case_count": len(cases),
            },
        ),
    )
    workspace = SourceWorkspace(Path(args.root).resolve(), max_files=200)
    interpreters = [RuleInterpreter()]
    if not args.no_model:
        for model in [m.strip() for m in args.models.split(",") if m.strip()]:
            interpreter = ModelInterpreter(OllamaConnector(model=model))
            interpreter.name = f"model:{model}"
            interpreters.append(interpreter)

    results, summary = [], {}
    for interpreter in interpreters:
        passed = action_correct = failures = 0
        failed_ids = []
        for case in cases:
            started = time.perf_counter()
            intent = interpreter.interpret(case["text"])
            seconds = round(time.perf_counter() - started, 3)
            evidence = getattr(interpreter, "last_evidence", {})
            model_failed = evidence.get("status") == "failed"
            failures += model_failed
            request = resolve_request(case["text"], intent, workspace, interpreter.name)
            checks = check_case(case, request)
            action_correct += checks["action"]
            ok = all(checks.values())
            passed += ok
            if not ok:
                failed_ids.append(case["id"])
            results.append(
                {
                    "interpreter": interpreter.name,
                    "id": case["id"],
                    "text": case["text"],
                    "expected": case["expected"],
                    "raw_intent": intent.model_dump(),
                    "resolved": request.model_dump(),
                    "checks": checks,
                    "passed": ok,
                    "model_failed": model_failed,
                    "seconds": seconds,
                    "model_reply": evidence.get("response", {}).get("message", {}).get("content")
                    if evidence
                    else None,
                }
            )
        summary[interpreter.name] = {
            "requests": len(cases),
            "action_correct": action_correct,
            "all_checks_passed": passed,
            "model_failures": failures,
            "failed_ids": failed_ids,
        }
        print(f"{interpreter.name}: {summary[interpreter.name]}", flush=True)
        if hasattr(interpreter, "connector"):
            interpreter.connector.unload()
    write_json(out / "results.json", {"summary": summary, "results": results})

    lines = [
        f"# Request interpretation — {cases_path.name}",
        "",
        f"Requests: {len(cases)}. Workspace: {Path(args.root).name}.",
        "",
        "| Interpreter | Action correct | All checks passed | Model failures | Failed IDs |",
        "|---|---|---|---|---|",
    ]
    for name, s in summary.items():
        lines.append(
            f"| {name} | {s['action_correct']}/{s['requests']} | "
            f"{s['all_checks_passed']}/{s['requests']} | {s['model_failures']} | "
            f"{', '.join(s['failed_ids']) or '-'} |"
        )
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
