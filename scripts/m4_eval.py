"""Milestone 4 — held-out evaluation on the supervisor's security lab.

This is the first run of the FROZEN M3 system on data it was never tuned on
(TestData/security_lab, provided by the supervisor). The detector configuration is not
changed here; the script only measures and records. Ground truth is the lab's own
manifest plus the intentional SQLi sinks marked in its source.

Scope: the thesis tool targets CWE-95 / CWE-78 / CWE-89 only. The lab's injection flaws
are all SQL injection (CWE-89); its XSS scenarios (CWE-79) are out of scope and are
reported as a coverage gap, not counted as detector misses.

A key structural fact about this lab: every SQL statement is executed through the
project's own ``query(...)`` / ``sql_project(...)`` helper, never through a bare
``cursor.execute(...)``. The frozen Semgrep taint rule sinks on ``cursor.execute``, so
this run measures how the system generalises to an application it did not anticipate.
"""

import argparse
import hashlib
from pathlib import Path

from vuln_assistant.analysis import Detection
from vuln_assistant.evidence import ROOT, environment_manifest, run_directory, write_json
from vuln_assistant.metrics import scores
from vuln_assistant.model import DEFAULT_MODEL, KNOWN_DIGESTS, OllamaConnector
from vuln_assistant.pipeline import Analyzer
from vuln_assistant.review import ModelReviewer
from vuln_assistant.scanners import make_scanner
from vuln_assistant.workspace import SourceWorkspace

# App source files to analyse (tests, caches and the thin project wrappers are excluded;
# the wrappers only call core.sql_project, which is analysed directly in core.py).
SOURCE_FILES = [
    "advanced.py",
    "app.py",
    "content.py",
    "core.py",
    "platform_lab.py",
    "runtime_services.py",
    "seed_data.py",
    "smtp_local.py",
    "ui.py",
    "workflows.py",
]

# In-scope SQLi ground truth. Each sink is located at run time by a unique code needle,
# so the record is robust to line-number drift. Family is CWE-89 for all of them.
SQLI_SINKS = [
    ("advanced.py", "c.name LIKE '%\"+q+\"%' GROUP BY", "LAB-02 contacts LIKE"),
    ("advanced.py", "p.category='\"+cp['scope']", "LAB-03 coupon scope (second-order)"),
    ("advanced.py", "t.priority='+str(priority)", "LAB-04 triage priority"),
    ("advanced.py", "ORDER BY '+sort", "LAB-05 payroll ORDER BY"),
    ("core.py", "= '+literal", "core.sql_project (/pNN/lab)"),
    ("platform_lab.py", "LIKE '%\"+q+\"%' ORDER BY i.id", "platform items LIKE"),
    ("platform_lab.py", "status = '\"+expression+\"'", "platform status filter"),
]
# Out-of-scope scenarios (CWE-79), reported as a coverage gap, never as a miss.
XSS_SCENARIOS = ["LAB-01", "LAB-06", "LAB-07", "LAB-08", "LAB-09", "LAB-10"]

MATCH_WINDOW = 4  # a CWE-89 detection matches a sink if within this many lines of it


def resolve_sinks(root: Path) -> list[dict]:
    resolved = []
    for file, needle, note in SQLI_SINKS:
        text = (root / file).read_text(encoding="utf-8").splitlines()
        hits = [i + 1 for i, line in enumerate(text) if needle in line]
        if len(hits) != 1:
            raise RuntimeError(f"Ground-truth needle not unique in {file}: {needle!r} -> {hits}")
        resolved.append({"file": file, "line": hits[0], "note": note})
    return resolved


def in_scope_detections(detections: list[Detection]) -> list[Detection]:
    return [d for d in detections if d.family == "CWE-89"]


def score_condition(sinks: list[dict], detections: list[dict]) -> dict:
    """detections: list of {path, line, detected_by}. Match to sinks within the window."""
    matched_sink_ids, matched_det_ids = set(), set()
    for si, sink in enumerate(sinks):
        for di, det in enumerate(detections):
            if (
                det["path"].endswith(sink["file"])
                and abs(det["line"] - sink["line"]) <= MATCH_WINDOW
            ):
                matched_sink_ids.add(si)
                matched_det_ids.add(di)
    tp = len(matched_sink_ids)
    fn = len(sinks) - tp
    fp = len(detections) - len(matched_det_ids)
    # No clean TN set on a whole application; report counts plus precision/recall only.
    counts = {"tp": tp, "fp": fp, "tn": 0, "fn": fn}
    result = scores(counts)
    result.pop("accuracy")  # undefined without a negative set on free-form source
    result["found_sinks"] = sorted(sinks[i]["note"] for i in matched_sink_ids)
    result["missed_sinks"] = sorted(
        sinks[i]["note"] for i in range(len(sinks)) if i not in matched_sink_ids
    )
    result["false_positive_lines"] = sorted(
        f"{detections[i]['path']}:{detections[i]['line']}"
        for i in range(len(detections))
        if i not in matched_det_ids
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=str(ROOT / "TestData/security_lab"))
    parser.add_argument("--models", default=DEFAULT_MODEL, help="comma-separated Ollama tags")
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--out")
    parser.add_argument(
        "--explore-model-max-chars",
        type=int,
        default=60000,
        help="exploratory extra pass: raise the model file-size limit so it also sees "
        "large files like advanced.py (not the frozen config)",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = run_directory("artifacts/m4", "lab", args.out)
    print(f"Evidence: {out}", flush=True)

    files = [f for f in SOURCE_FILES if (root / f).is_file()]
    sinks = resolve_sinks(root)
    lab_hashes = {
        f: hashlib.sha256((root / f).read_bytes()).hexdigest()
        for f in sorted({*files, "vulnerability_manifest.json"})
        if (root / f).is_file()
    }
    write_json(
        out / "manifest.json",
        environment_manifest(
            "M4 held-out evaluation on the supervisor security lab; detector frozen, no tuning",
            {
                "args": vars(args),
                "lab_root": str(root),
                "held_out_file_sha256": lab_hashes,
                "ground_truth_sqli_sinks": sinks,
                "xss_scenarios_out_of_scope": XSS_SCENARIOS,
                "note": "Every SQL sink in the lab runs through the query() helper, "
                "not cursor.execute(); the frozen Semgrep rule targets cursor.execute.",
            },
        ),
    )
    workspace = SourceWorkspace(root, max_files=200)

    def run(scanners, reviewer, label: str) -> dict:
        analyzer = Analyzer(workspace, scanners, reviewer, language="hu")
        detections, per_file, problems = [], {}, []
        for rel in files:
            analysis, file_problems = analyzer.analyse_file(rel)
            problems += file_problems
            per_file[rel] = {
                "model": analysis.model.status,
                "cwe89": [
                    {"line": d.line, "detected_by": d.detected_by, "code": d.code_line}
                    for d in in_scope_detections(analysis.detections)
                ],
            }
            for d in in_scope_detections(analysis.detections):
                detections.append({"path": rel, "line": d.line, "detected_by": d.detected_by})
        write_json(out / f"detections-{label}.json", {"per_file": per_file, "problems": problems})
        result = score_condition(sinks, detections)
        if reviewer is not None:
            result["model_ran_files"] = sorted(
                f for f, v in per_file.items() if v["model"] == "completed"
            )
            result["model_skipped_files"] = sorted(
                f for f, v in per_file.items() if v["model"] == "skipped"
            )
        return result

    layers = {"semgrep": ("semgrep",), "union": ("bandit", "semgrep")}
    results = {}

    def scanners_for(layer):
        return [make_scanner(t, workspace, "m3") for t in layers[layer]]

    for layer in layers:
        results[f"{layer} (no AI)"] = run(scanners_for(layer), None, f"{layer}-noai")

    if not args.no_model:
        for model in [m.strip() for m in args.models.split(",") if m.strip()]:
            connector = OllamaConnector(model=model)
            reviewer = ModelReviewer(connector)
            reviewer.identify(KNOWN_DIGESTS.get(model))
            try:
                for layer in layers:
                    results[f"{layer} + {model}"] = run(
                        scanners_for(layer), reviewer, f"{layer}-{model.replace(':', '_')}"
                    )
                # Exploratory: let the model also see large files (NOT the frozen config).
                explorer = ModelReviewer(connector)
                explorer.identify(KNOWN_DIGESTS.get(model))
                explorer.max_chars = args.explore_model_max_chars
                explorer.max_lines = 2000
                results[f"union + {model} [explore: large files]"] = run(
                    scanners_for("union"), explorer, f"explore-{model.replace(':', '_')}"
                )
            finally:
                connector.unload()

    write_json(
        out / "metrics.json",
        {
            "in_scope_sqli_sinks": len(sinks),
            "xss_scenarios_out_of_scope": len(XSS_SCENARIOS),
            "conditions": results,
        },
    )

    lines = [
        "# M4 held-out evaluation — supervisor security lab",
        "",
        (
            f"In-scope SQLi sinks (ground truth): {len(sinks)}. "
            f"Out-of-scope XSS scenarios: {len(XSS_SCENARIOS)} (not targeted by the tool)."
        ),
        "Detector frozen (M3 configuration); this run performs no tuning.",
        "",
        "| Condition | TP | FP | FN | Precision | Recall |",
        "|---|---|---|---|---|---|",
    ]
    for name, r in results.items():
        lines.append(
            f"| {name} | {r['tp']} | {r['fp']} | {r['fn']} | {r['precision']} | {r['recall']} |"
        )
    lines += [
        "",
        (
            f"Recall denominator = {len(sinks)} in-scope SQLi sinks. "
            "FP = CWE-89 detections not matching any labelled sink (listed in metrics.json)."
        ),
        (
            f"XSS coverage by design: 0 of {len(XSS_SCENARIOS)} scenarios "
            "(CWE-79 is outside the tool's three families)."
        ),
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
