"""Evaluation on the 18 development samples (data/samples).

The samples, rules and prompts were developed together, so these numbers are optimistic.
The independent test is scripts/eval_lab.py.

Conditions (unit: one file with respect to its labelled family):
  basic:*                    the first, narrow scanner setup, for reference
  full:bandit, full:semgrep  each scanner alone
  full:scanners              union of both scanners
  <layer>+<model>#rN         scanner layer ("union" or "semgrep") plus the model reviewer,
                             with verification of model-only claims (repeat N); the model
                             sees hints only from the scanners of that layer
  <layer>+<model>-noverify   the same without the verification call (one run)
  model-accepted:<...>       accepted model issues alone (the model still saw the hints)
"""

import argparse
import csv
import hashlib
import json
import statistics

from vulnscan.analysis import merge
from vulnscan.metrics import evaluate
from vulnscan.model import DEFAULT_MODEL, KNOWN_DIGESTS, OllamaConnector
from vulnscan.review import ModelReviewer
from vulnscan.runinfo import ROOT, environment_manifest, run_directory, write_json
from vulnscan.scanners import make_scanner
from vulnscan.workspace import SourceWorkspace

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
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--models", default=DEFAULT_MODEL, help="comma-separated Ollama tags")
    parser.add_argument("--layers", default="union,semgrep")
    parser.add_argument("--no-ablation", action="store_true")
    parser.add_argument("--lang", default="hu", choices=["hu", "en"])
    parser.add_argument("--out")
    args = parser.parse_args()
    out = run_directory("dev_eval", args.out)
    print(f"Output: {out}", flush=True)
    corpus = ROOT / "data/samples"
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    write_json(
        out / "manifest.json",
        environment_manifest(
            "Evaluation on the development samples",
            {"args": vars(args), "corpus_split": manifest["split"]},
        ),
    )
    workspace = SourceWorkspace(corpus)
    for case in cases:
        data = workspace.resolve(case["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != case["sha256"]:
            raise RuntimeError(f"Sample file changed: {case['id']}")

    reports = {}
    for profile in ("basic", "full"):
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
        print(f"Scanned the samples with the {profile} setup", flush=True)

    def scanner_prediction(profile, tools, case):
        return any(
            f.family == case["cwe"]
            for tool in tools
            for f in reports[(profile, tool, case["id"])].findings
        )

    conditions: dict[str, dict[str, bool]] = {}
    for profile in ("basic", "full"):
        for name, tools in (
            ("bandit", ["bandit"]),
            ("semgrep", ["semgrep"]),
            ("scanners", ["bandit", "semgrep"]),
        ):
            conditions[f"{profile}:{name}"] = {
                c["id"]: scanner_prediction(profile, tools, c) for c in cases
            }

    layer_tools = {"union": ("bandit", "semgrep"), "semgrep": ("semgrep",)}
    layer_condition = {"union": "full:scanners", "semgrep": "full:semgrep"}
    layers = [layer.strip() for layer in args.layers.split(",") if layer.strip()]
    models = [model.strip() for model in args.models.split(",") if model.strip()]
    model_stats = {"requested": not args.no_model, "models": {}}
    explanation_rows = {}

    def run_model(reviewer, model, layer, label, keep_files):
        tools = layer_tools[layer]
        combined, accepted_only = {}, {}
        stats = {"failed": 0, "skipped": 0, "accepted": 0, "rejected_ungrounded": 0,
                 "rejected_by_verification": 0, "verification_calls": 0,
                 "verification_failures": 0, "line_corrected": 0, "dismissed": 0,
                 "unknown_refs": 0, "seconds": []}  # fmt: skip
        rows = []
        for case in cases:
            scans = [reports[("full", tool, case["id"])] for tool in tools]
            findings = [f for scan in scans for f in scan.findings]
            source = workspace.resolve(case["path"]).read_bytes()
            outcome, refs, lines = reviewer.review(source, findings, args.lang)
            detections = merge(case["path"], lines, scans, outcome, refs)
            combined[case["id"]] = any(d.family == case["cwe"] for d in detections)
            accepted_only[case["id"]] = any(a.issue.family == case["cwe"] for a in outcome.accepted)
            if outcome.status in ("failed", "skipped"):
                stats[outcome.status] += 1
            stats["accepted"] += len(outcome.accepted)
            for item in outcome.rejected:
                key = (
                    "rejected_by_verification"
                    if item.reason.startswith("not confirmed")
                    else (
                        "verification_failures"
                        if item.reason.startswith("verification failed")
                        else "rejected_ungrounded"
                    )
                )
                if key != "verification_failures":
                    stats[key] += 1
            stats["verification_calls"] += outcome.verification_calls
            stats["verification_failures"] += outcome.verification_failures
            stats["line_corrected"] += sum(a.line_corrected for a in outcome.accepted)
            stats["dismissed"] += len(outcome.dismissed)
            stats["unknown_refs"] += len(outcome.unknown_refs)
            if outcome.seconds is not None:
                stats["seconds"].append(outcome.seconds)
            safe = model.replace(":", "_").replace("/", "_")
            write_json(
                out / "model" / safe / f"{label}-{case['id']}.json",
                {
                    "outcome": outcome.model_dump(),
                    "detections": [d.model_dump() for d in detections],
                },
            )
            if keep_files:
                rows.append((case, detections, outcome))
        seconds = stats.pop("seconds")
        if seconds:
            stats["seconds_median"] = round(statistics.median(seconds), 3)
            stats["seconds_max"] = round(max(seconds), 3)
            stats["seconds_total"] = round(sum(seconds), 3)
        print(f"{model} {label}: {stats}", flush=True)
        return combined, accepted_only, stats, rows

    if not args.no_model:
        for model in models:
            connector = OllamaConnector(model=model)
            reviewer = ModelReviewer(connector)
            entry = {"metadata": reviewer.identify(KNOWN_DIGESTS.get(model)), "runs": {}}
            model_stats["models"][model] = entry
            try:
                for layer in layers:
                    runs = []
                    for repeat in range(1, args.repeats + 1):
                        label = f"{layer}#r{repeat}"
                        combined, accepted_only, stats, rows = run_model(
                            reviewer, model, layer, label, repeat == 1 and layer == "union"
                        )
                        conditions[f"{layer}+{model}#r{repeat}"] = combined
                        conditions[f"model-accepted:{layer}+{model}#r{repeat}"] = accepted_only
                        entry["runs"][label] = stats
                        runs.append(combined)
                        if rows:
                            explanation_rows[model] = rows
                    entry[f"unstable_cases:{layer}"] = sorted(
                        c["id"] for c in cases if len({run[c["id"]] for run in runs}) > 1
                    )
                if not args.no_ablation and "union" in layers:
                    reviewer.verify = False
                    combined, _, stats, _ = run_model(
                        reviewer, model, "union", "union-noverify", False
                    )
                    conditions[f"union+{model}-noverify"] = combined
                    entry["runs"]["union-noverify"] = stats
                    reviewer.verify = True
            finally:
                connector.unload()

    changes = {}
    for name, predictions in conditions.items():
        layer = name.split("+", 1)[0]
        if "+" not in name or name.startswith("model-accepted") or layer not in layer_condition:
            continue
        base = conditions[layer_condition[layer]]
        changes[name] = {
            "new_true_positives": [c["id"] for c in cases if c["expected_vulnerable"] and predictions[c["id"]] and not base[c["id"]]],
            "new_false_positives": [c["id"] for c in cases if not c["expected_vulnerable"] and predictions[c["id"]] and not base[c["id"]]],
        }  # fmt: skip

    results = {}
    for name, predictions in conditions.items():
        result = metrics_for(cases, predictions)
        result["sklearn_agrees"] = sklearn_check(cases, predictions, result["overall"])
        results[name] = result
    write_json(
        out / "metrics.json",
        {"conditions": results, "changes_vs_scanner_layer": changes, "model": model_stats},
    )

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
            "# Development samples",
            "",
            f"Cases: {len(cases)} (6 vulnerable, 12 non-vulnerable). Unit: file w.r.t. its labelled family.",
            "",
            *table,
            "",
            "Model statistics: see metrics.json.",
        ]
    )
    (out / "summary.md").write_text(summary + "\n", encoding="utf-8")

    for model, rows in explanation_rows.items():
        sheet = [
            f"# Explanation review sheet — {model}, union layer, repeat 1",
            "",
            "Score each explanation by hand.",
            "",
        ]
        for case, detections, outcome in rows:
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
                    f"- Rejected {item.issue.family} line {item.issue.line}: {item.reason}"
                )
            sheet.append("")
        safe = model.replace(":", "_").replace("/", "_")
        (out / f"explanations-{safe}.md").write_text("\n".join(sheet), encoding="utf-8")

    print(summary, flush=True)


if __name__ == "__main__":
    main()
