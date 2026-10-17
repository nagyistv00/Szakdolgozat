"""Milestone 3 development run on the 18-case development corpus (data/m2).

NOT a final evaluation: these cases, rules and prompts influenced development, so the
numbers are optimistic development observations. The final, held-out evaluation is M4.

Conditions (case level, unit = one file w.r.t. its labelled family):
  m2:*                    milestone 2 scanner configuration, for reference
  m3:bandit / m3:semgrep  milestone 3 baseline scanners alone
  m3:scanners             union of both baseline scanners (the system without AI)
  m3:scanners+model#rN    the same scanners plus the model reviewer (repeat N)
  model-accepted#rN       diagnostic only: grounded model issues alone (the model saw
                          the scanner hints, so this is not an independent model-only run)
"""

import argparse
import csv
import hashlib
import json
import statistics

from vuln_assistant.analysis import merge
from vuln_assistant.evidence import ROOT, environment_manifest, run_directory, write_json
from vuln_assistant.metrics import evaluate
from vuln_assistant.model import DEFAULT_MODEL, KNOWN_DIGESTS, OllamaConnector
from vuln_assistant.review import ModelReviewer
from vuln_assistant.scanners import make_scanner
from vuln_assistant.workspace import SourceWorkspace

FAMILIES = ("CWE-95", "CWE-78", "CWE-89")
RUBRIC = (
    "| Criterion | Score (0/1) |\n|---|---|\n| Correct family | |\n| Correct line | |\n"
    "| Correct input source | |\n| Fix is correct and safe | |\n| Understandable | |\n"
)


def metrics_for(cases, predictions: dict[str, bool]) -> dict:
    result = {
        "overall": evaluate(
            [c["expected_vulnerable"] for c in cases], [predictions[c["id"]] for c in cases]
        )
    }
    for family in FAMILIES:
        subset = [c for c in cases if c["cwe"] == family]
        result[family] = evaluate(
            [c["expected_vulnerable"] for c in subset], [predictions[c["id"]] for c in subset]
        )
    return result


def sklearn_check(cases, predictions: dict[str, bool], ours: dict) -> bool:
    """Independent cross-check of the hand-written metric code."""
    from sklearn.metrics import accuracy_score, precision_score, recall_score

    y_true = [c["expected_vulnerable"] for c in cases]
    y_pred = [predictions[c["id"]] for c in cases]
    pairs = [
        (ours["accuracy"], accuracy_score(y_true, y_pred)),
        (ours["precision"], precision_score(y_true, y_pred, zero_division=0)),
        (ours["recall"], recall_score(y_true, y_pred, zero_division=0)),
    ]
    return all(a is None or abs(a - b) < 1e-3 for a, b in pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--lang", default="hu", choices=["hu", "en"])
    parser.add_argument("--out")
    args = parser.parse_args()
    out = run_directory("artifacts/m3", "dev", args.out)
    print(f"Evidence: {out}", flush=True)
    corpus = ROOT / "data/m2"
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    write_json(
        out / "manifest.json",
        environment_manifest(
            "M3 development run on the development corpus; not a final evaluation",
            {"args": vars(args), "corpus_split": manifest["split"]},
        ),
    )
    workspace = SourceWorkspace(corpus)
    for case in cases:
        data = workspace.resolve(case["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != case["sha256"]:
            raise RuntimeError(f"Corpus hash changed: {case['id']}")

    reports = {}
    for profile in ("m2", "m3"):
        for tool in ("bandit", "semgrep"):
            scanner = make_scanner(tool, workspace, profile)
            for case in cases:
                report = scanner.scan(case["path"])
                if report.status != "completed":
                    raise RuntimeError(f"{profile}:{tool} failed on {case['id']}: {report.errors}")
                reports[(profile, tool, case["id"])] = report
                write_json(
                    out / "scans" / f"{profile}-{tool}-{case['id']}.json", report.model_dump()
                )
        print(f"Scanned development corpus with the {profile} profile", flush=True)

    def scanner_prediction(profile, tools, case):
        return any(
            f.family == case["cwe"]
            for tool in tools
            for f in reports[(profile, tool, case["id"])].findings
        )

    conditions: dict[str, dict[str, bool]] = {}
    for profile in ("m2", "m3"):
        for name, tools in (
            ("bandit", ["bandit"]),
            ("semgrep", ["semgrep"]),
            ("scanners", ["bandit", "semgrep"]),
        ):
            conditions[f"{profile}:{name}"] = {
                c["id"]: scanner_prediction(profile, tools, c) for c in cases
            }

    model_stats = {"requested": not args.no_model}
    explanation_rows = []
    if not args.no_model:
        connector = OllamaConnector(model=args.model)
        reviewer = ModelReviewer(connector)
        model_stats["metadata"] = reviewer.identify(KNOWN_DIGESTS.get(args.model))
        model_stats["repeats"] = []
        try:
            for repeat in range(1, args.repeats + 1):
                combined, accepted_only = {}, {}
                stats = {"failed": 0, "skipped": 0, "accepted": 0, "rejected": 0,
                         "line_corrected": 0, "dismissed": 0, "unknown_refs": 0, "seconds": []}  # fmt: skip
                for case in cases:
                    scans = [reports[("m3", tool, case["id"])] for tool in ("bandit", "semgrep")]
                    findings = [f for scan in scans for f in scan.findings]
                    source = workspace.resolve(case["path"]).read_bytes()
                    outcome, refs, lines = reviewer.review(source, findings, args.lang)
                    detections = merge(case["path"], lines, scans, outcome, refs)
                    combined[case["id"]] = any(d.family == case["cwe"] for d in detections)
                    accepted_only[case["id"]] = any(
                        a.issue.family == case["cwe"] for a in outcome.accepted
                    )
                    if outcome.status in ("failed", "skipped"):
                        stats[outcome.status] += 1
                    stats["accepted"] += len(outcome.accepted)
                    stats["rejected"] += len(outcome.rejected)
                    stats["line_corrected"] += sum(a.line_corrected for a in outcome.accepted)
                    stats["dismissed"] += len(outcome.dismissed)
                    stats["unknown_refs"] += len(outcome.unknown_refs)
                    if outcome.seconds is not None:
                        stats["seconds"].append(outcome.seconds)
                    write_json(
                        out / "model" / f"r{repeat}-{case['id']}.json",
                        {
                            "outcome": outcome.model_dump(),
                            "detections": [d.model_dump() for d in detections],
                        },
                    )
                    if repeat == 1:
                        explanation_rows.append((case, detections, outcome))
                conditions[f"m3:scanners+model#r{repeat}"] = combined
                conditions[f"model-accepted#r{repeat}"] = accepted_only
                seconds = stats.pop("seconds")
                if seconds:
                    stats["seconds_median"] = round(statistics.median(seconds), 3)
                    stats["seconds_max"] = round(max(seconds), 3)
                    stats["seconds_total"] = round(sum(seconds), 3)
                model_stats["repeats"].append(stats)
                print(f"Model repeat {repeat}/{args.repeats} done: {stats}", flush=True)
        finally:
            connector.unload()
        runs = [conditions[f"m3:scanners+model#r{r}"] for r in range(1, args.repeats + 1)]
        model_stats["unstable_cases"] = sorted(
            c["id"] for c in cases if len({run[c["id"]] for run in runs}) > 1
        )

    results = {}
    for name, predictions in conditions.items():
        result = metrics_for(cases, predictions)
        result["sklearn_agrees"] = sklearn_check(cases, predictions, result["overall"])
        results[name] = result
    write_json(out / "metrics.json", {"conditions": results, "model": model_stats})

    with (out / "predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["case", "group", "cwe", "expected_vulnerable", *conditions])
        for case in cases:
            writer.writerow(
                [case["id"], case["group"], case["cwe"], case["expected_vulnerable"]]
                + [conditions[name][case["id"]] for name in conditions]
            )

    table = [
        "| Condition | TP | FP | TN | FN | Accuracy | Precision | Recall |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, result in results.items():
        o = result["overall"]
        table.append(
            f"| {name} | {o['tp']} | {o['fp']} | {o['tn']} | {o['fn']} | "
            f"{o['accuracy']} | {o['precision']} | {o['recall']} |"
        )
    summary = "\n".join(
        [
            "# M3 development run (development corpus — not a final evaluation)",
            "",
            f"Cases: {len(cases)} (6 vulnerable, 12 non-vulnerable). Unit: file w.r.t. its labelled family.",
            "",
            *table,
            "",
            "Model statistics: see metrics.json.",
        ]
    )
    (out / "summary.md").write_text(summary + "\n", encoding="utf-8")

    if explanation_rows:
        sheet = [
            "# Explanation review sheet (repeat 1)",
            "",
            "Score each model explanation manually; do not use the model to grade itself.",
            "",
        ]
        for case, detections, outcome in explanation_rows:
            sheet.append(
                f"## {case['id']} (label: {case['cwe']}, vulnerable={case['expected_vulnerable']})"
            )
            sheet.append(f"Model status: {outcome.status}")
            for d in detections:
                sheet.append(
                    f"- {d.family}, line {d.line}, by {', '.join(d.detected_by)}: `{d.code_line}`"
                )
                if d.explanation_source == "model":
                    sheet += [
                        f"  - Explanation: {d.explanation}",
                        f"  - Input source: {d.input_source}",
                        f"  - Fix: {d.fix}",
                        "",
                        RUBRIC,
                    ]
            for item in outcome.dismissed:
                sheet.append(f"- Dismissed {item.ref}: {item.reason}")
            for item in outcome.rejected:
                sheet.append(
                    f"- Rejected (ungrounded) {item.issue.family} line {item.issue.line}: {item.reason}"
                )
            sheet.append("")
        (out / "explanations.md").write_text("\n".join(sheet), encoding="utf-8")

    print(summary, flush=True)


if __name__ == "__main__":
    main()
