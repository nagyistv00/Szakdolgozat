# Development samples

18 short Python files for the three weakness families: for each family two vulnerable
cases, their two fixed versions and two negative controls that look dangerous but are not.
`manifest.json` gives every file's label, the reason for the label and its SHA-256 hash.

Assumptions behind the labels: `user_text` can come from an untrusted caller, and the SQL
examples use a standard `sqlite3` cursor. A "not vulnerable" label refers only to the
labelled weakness. The labels were checked by hand on 2026-10-25 (18 of 18 agreed).

These files shaped the rules and prompts, so results on them are development results, not
an independent test. The independent test data is in `data/lab` and
`data/requests_test.json`.

The files are only scanned, never imported or run.
