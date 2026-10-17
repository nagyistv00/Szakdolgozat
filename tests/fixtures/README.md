# Scanner installation fixtures

Original, project-authored synthetic Python snippets created on 2026-09-19.
They are static analysis inputs only: tests never import or execute them.

- `unsafe_eval.py`: direct use of `eval` on a function parameter, expected Bandit B307 and local Semgrep rule finding on line 2.
- `literal_only.py`: literal parsing without general code evaluation; expected no finding for the selected rule. This does not establish overall safety: resource exhaustion and other concerns are outside this smoke check.
- `text_only.py`: the suspicious expression appears only in a comment and a string; expected no syntax-level finding.

These three snippets check installation and JSON result handling only. They are not a vulnerability benchmark, training set, or evidence of general detection accuracy. Bandit is restricted to B307 and Semgrep to one locally authored rule; this is not a comparison of their complete rule sets.
