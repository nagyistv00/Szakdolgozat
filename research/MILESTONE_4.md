# Milestone 4 — held-out evaluation on the supervisor's security lab

Status on 2026-10-25: **set up; awaiting the first on-machine run.** This document records the
plan, the scope analysis and the frozen configuration. Measured results are added only after
`scripts/m4_check.ps1` has run on the target machine, in a dated section and in `RESEARCH_LOG.md`.

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

qwen2.5-coder:14b (digest `9ec8897f…68849`), Semgrep taint rules + full Bandit, structural
check and self-verification on, temperature 0, seed 0, Hungarian explanations. Identical to the
configuration frozen at the close of M3 (`research/MILESTONE_3.md`).

## Open items before M4 can be called complete

- Run `scripts/m4_check.ps1` on the target machine and record the measured results.
- 10–15 new, user-written natural-language requests, independent of the rule interpreter, for the
  language-control part of the evaluation.
- Human label review of the development corpus (open since M2) and manual scoring of explanations.
- M4 completion is the user's decision; this document does not claim the milestone is finished.
