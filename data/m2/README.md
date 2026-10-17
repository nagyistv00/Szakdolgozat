# Development corpus v1

18 original, assistant-authored Python snippets: six proposed vulnerable cases, their six paired fixes, and six contextual negative controls. Categories: CWE-95 (eval injection), CWE-78 (OS command injection) and CWE-89 (SQL injection). See `manifest.json` for each source hash, group, label rationale and origin.

All cases are **development data**. Labels are provisional source-inspection judgements, not independently verified ground truth. Human review is pending. The functions assume that `user_text` can be supplied by an untrusted caller, and SQL examples assume a normal sqlite3-compatible cursor. Negative labels concern only the specified weakness, not overall safety.

Do not execute or import the samples. The source describes unsafe operations solely so static analyzers can inspect it. No live target or external repository is scanned by the diagnostic.

The six groups with a `bad` and `fixed` member must remain together in any later split. The entire current corpus has already influenced development, so **none of it can be presented as an unseen final test set**. No training set is needed under the user's current no-training decision. Final evaluation needs new independently reviewed cases, preferably including real vulnerable/fixed revisions with documented provenance and use permissions.

The local Semgrep rules deliberately have narrow syntactic coverage. Alias-based eval, concatenated SQL and contextual negative cases expose limitations; do not change labels to match tool outputs. Do not tune the rules merely to obtain perfect results on these examples. Bandit reports its own CWE mapping, which is preserved even when the corpus uses a more specific category.

`requests.json` contains 12 Hungarian/English workflow acceptance scenarios for milestone 3. They are specifications, not passed natural-language tests. The current code has no user-request interpreter.

Conceptual references (no source code copied):

- https://cwe.mitre.org/data/definitions/95.html
- https://cwe.mitre.org/data/definitions/78.html
- https://cwe.mitre.org/data/definitions/89.html
- https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html
- https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html
- https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html
