# Milestone 4 — held-out evaluation on the supervisor's security lab

Status on 2026-10-25: **all planned M4 measurements complete** — lab detection run, held-out
request run, manual explanation scoring and dev-corpus label review (results below). Closing
the milestone is the user's decision. This document records the plan, the scope analysis, the frozen configuration and
the measured results; details and interpretation are in `RESEARCH_LOG.md`.

## Data

The supervisor provided a local, intentionally vulnerable teaching app at
`TestData/security_lab` (received 2026-10-25). It ships its own ground truth:
`vulnerability_manifest.json` (ten app scenarios LAB-01…LAB-10) and `# VULN` / `SZÁNDÉKOS`
markers in the source. This is genuinely held out: the M3 rules, prompts and model were frozen
on 2026-10-17 and never tuned on this app. The evaluation script records a SHA-256 of every
analysed file before the run and performs no tuning.

The lab also contains `source/code_vulnerabilities.csv` (1000 generic SQLi/XSS snippets) and
`source/analysis.json`; these look like a separate generic ML dataset and are **not** used as
the evaluation target here — the app source is what the tool analyses.

## Scope: what the tool can and cannot be credited for

The thesis tool targets three weakness families: CWE-95, CWE-78, CWE-89. The lab's flaws are:

- **SQL injection (CWE-89) — in scope, 7 intentional sinks:** LAB-02 (`advanced.py` contacts
  LIKE), LAB-03 (`advanced.py` coupon scope, second-order), LAB-04 (`advanced.py` triage
  priority), LAB-05 (`advanced.py` payroll ORDER BY), the generic `core.sql_project` behind the
  `/pNN/lab` routes, and two more in `platform_lab.py` (items LIKE, status filter).
- **XSS (CWE-79) — out of scope, 6 scenarios** (LAB-01, 06, 07, 08, 09, 10) plus reflected/
  stored/DOM variants in `core.xss_project`. Reported as a coverage gap, never as a miss.

No eval/exec (CWE-95) or OS command injection (CWE-78) is present in the lab.

**Structural fact that drives the result:** every SQL statement is executed through the
project's own `query(...)` / `sql_project(...)` helper, never through a bare
`cursor.execute(...)`. The only literal `db.execute(...)` is the safe, parameterized wrapper in
`core._execute`. The frozen Semgrep taint rule sinks on `cursor.execute`, so it is expected to
miss these flows; detection, if any, must come from Bandit B608 (string-built SQL) or the model.
The model reviewer's frozen size limit (20000 characters) also skips `advanced.py` (~23.6 KB),
so on the largest file the model does not engage under the frozen config. This is exactly the
generalisation question M4 is meant to answer; the rules are **not** changed to fit the lab.

## What is NOT part of this evaluation

The lab runs a live HTTP server with exploitable endpoints; the supervisor supplied a working
SQL-injection payload for `/p04/triage`. The thesis tool is a static source-code analyzer, so
the evaluation reads the lab's source files only. Actively sending the payload to the running
server (data exfiltration against a live service) is outside the tool's purpose and is not
performed. This keeps the measurement aligned with what the thesis claims.

## Method

`scripts/m4_eval.py` runs the frozen system over the app's `.py` files and matches each CWE-89
detection to the labelled sinks (same file, within 4 lines). Conditions: scanner layer
`semgrep` and `union` (Bandit ∪ Semgrep), each without and with the model (14B default, 7B
reference), plus one clearly-labelled exploratory pass that raises the model file-size limit so
it also sees `advanced.py` (not the frozen config). Reported per condition: TP / FP / FN,
precision, recall, which sinks were found or missed, and the false-positive lines. Accuracy is
omitted: a whole application has no clean negative set. XSS coverage is reported as 0 / 6 by
design.

## Frozen configuration under test

qwen2.5-coder:14b (digest `9ec8897f…68849`), **Semgrep taint rules as the scanner layer**,
structural check and self-verification on, temperature 0, seed 0, Hungarian explanations —
identical to the configuration frozen at the close of M3 (`research/MILESTONE_3.md`). Baseline
without AI: Semgrep taint alone. Bandit (full set) is a **reference**, run in the union layer.
(Correction 2026-10-25: an earlier version of this document wrongly listed "Semgrep + full
Bandit" as the frozen layer and marked the union row as the frozen system.)

## Results — 2026-10-25 (artifacts/m4/lab-20261025T154631Z)

All steps exited 0 (git, ruff, pytest 94/94, m4_eval). 7 labelled SQLi sinks, match window ±4.

| Condition | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|
| Semgrep (no AI) | 0 | 1 | 7 | 0.000 | 0.000 |
| Bandit ∪ Semgrep (no AI) | 4 | 3 | 3 | 0.571 | 0.571 |
| **Semgrep + 14B (frozen system)** | **0** | **1** | **7** | **0.000** | **0.000** |
| Bandit ∪ Semgrep + 14B (Bandit reference added) | 4 | 3 | 3 | 0.571 | 0.571 |
| same, exploratory: model sees large files | 4 | 3 | 3 | 0.571 | 0.571 |
| Semgrep + 7B | 0 | 5 | 7 | 0.000 | 0.000 |
| Bandit ∪ Semgrep + 7B | 4 | 7 | 3 | 0.364 | 0.571 |
| same, exploratory | 4 | 8 | 3 | 0.333 | 0.571 |

- Found (all by Bandit B608): LAB-04, LAB-05, core.sql_project, platform status filter.
- Missed: LAB-02, LAB-03 (second-order), platform items LIKE — the query is built in two steps
  (`base` + a fragment that does not start with an SQL keyword), invisible to B608; Semgrep's
  sink is `cursor.execute`, while the lab routes everything through `query()`.
- The frozen system (Semgrep + 14B) finds **none** of the 7 sinks; its only CWE-89 report is
  core.py:23, inside the `_execute` wrapper (every parameter is a taint source), which the 14B
  model also endorses. Adding the Bandit reference gives 4/7 plus two more false positives:
  core.py:77 (whitelisted column name) and runtime_services.py:20 (table name from a constant list).
- The 14B model added no true positive and no false positive; it only confirmed Bandit findings,
  even when allowed to see `advanced.py` and `ui.py`. The 7B added 4–5 false positives on safe
  `?`-parameterised `query()` calls. The frozen size limit skipped both `advanced.py` and `ui.py`.
- Reading: the model's detection gain seen on the development corpus (aliased eval) did not
  generalise to this application. The frozen system scores 0/7 here; every true positive comes
  from the Bandit reference. With or without Bandit, the model changes no count. No rule,
  prompt or limit was changed in response; candidate improvements are recorded as future work.

## Results — held-out requests (artifacts/m4/requests-20261025T160933Z)

| Interpreter | Action correct | All checks passed | Failed |
|---|---|---|---|
| rules | 9/14 | 9/14 | H-01, H-03, H-06, H-11, H-12 |
| qwen2.5-coder:14b | 13/14 | 13/14 | H-11 |
| qwen2.5-coder:7b | 13/14 | 13/14 | H-11 |

- The rule baseline misses paraphrased analyse/explain requests and lets an instruction-override
  request (H-12, "follow them") through as an analysis; both model interpreters handle all of
  these, H-12 included.
- H-11 (rewrite request): both models proposed the correct `reject_unsupported_action`, but the
  deterministic fabrication guard (`írd … biztonságos`) takes precedence and relabels it as
  `reject_result_fabrication` — still rejected, wrong category. The guard pattern is too broad;
  recorded as future work, not changed.
- Reading: unlike detection, the model gives a real, generalising gain in request
  interpretation (9/14 → 13/14 on unseen requests; 12/12 for all three on the dev set).

## Results — manual explanation scoring and label review (artifacts/m4/manual-20261025)

Scored by the author (human) on a dedicated scoring page; nothing was pre-filled. Material: the
frozen 14B model's 12 Hungarian explanations from the M3 closing run (union layer, repeat 1).

| Criterion | All (12) | True-positive findings (7) | False-positive findings (5) |
|---|---|---|---|
| Correct family | 7 | 7 | 0 |
| Correct line | 10 | 7 | 3 |
| Correct input source | 11 | 7 | 4 |
| Fix correct and safe | **2** | **2** | 0 |
| Understandable | 12 | 7 | 5 |
| **Total** | **42/60 (70%)** | **30/35 (86%)** | **12/25 (48%)** |

- Localisation and clarity are strong; the suggested fix is the weak point (2/7 on real
  findings): `%s` placeholders that fail with sqlite3 (3×) and POSIX-only `shlex.quote` advice
  (2×). On false positives the model proposes unnecessary, sometimes behaviour-changing fixes.
- Label review of the 18 development cases: 18 agree, 0 disagree, 0 unsure (with stated
  assumptions). The reviewer is the author, not a third party; the corpus stays development data.

## Open items before M4 can be called complete

- Natural-language requests: **received** — `TestData/m4_requests.json`, 14 held-out requests
  (7 HU, 7 EN; generated by an external assistant from a category brief, labels supplied by the
  user). Scored by `scripts/m4_requests_eval.py` with a protocol fixed before the first run
  (action, language, focus always; target only for `analyse`/`target_not_found`; finding index
  only for `explain_existing`). Run: `./scripts/m4_check.ps1 -RequestsOnly`. **Done** (above).
- Human label review of the development corpus and manual scoring of explanations: **done**
  (above).
- M4 completion is the user's decision; this document does not claim the milestone is finished.
