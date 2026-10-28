# Fixtures for the installation checks

Three tiny Python files used by `tests/test_install.py`. The tests only scan them; they are
never imported or run.

- `unsafe_eval.py`: `eval` on a function parameter. Bandit B307 and the Semgrep smoke rule
  should both report line 2.
- `literal_only.py`: parses a literal without general evaluation. No finding is expected.
- `text_only.py`: the suspicious call appears only in a comment and a string. No finding is
  expected.

They check that the tools are installed and that their JSON output is read correctly. They
are not an accuracy benchmark.
