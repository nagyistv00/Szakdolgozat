"""Scanner setup: family mapping, portable rule IDs and the taint rules.

The real-tool tests use small snippets written for these checks; they validate rule
semantics and are not evaluation data.
"""

import json
import os
import subprocess

import pytest

from vulnscan.scanners import BANDIT_FAMILY, make_scanner, normalise_semgrep_rule
from vulnscan.workspace import SourceWorkspace, TargetError, TargetNotFound


def fake_run(payload: dict, code: int):
    def run(command, **kwargs):
        return subprocess.CompletedProcess(command, code, json.dumps(payload), "")

    return run


def test_semgrep_rule_id_is_portable_and_family_comes_from_metadata(monkeypatch, tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x = 1\n", encoding="utf-8")
    payload = {
        "errors": [],
        "paths": {"scanned": [str(path)]},
        "results": [
            {
                "path": str(path),
                "check_id": "C.Users.someone.Documents.project.rules.python-sql-injection",
                "start": {"line": 1},
                "extra": {"severity": "ERROR", "message": "m", "metadata": {"cwe": "CWE-89"}},
            }
        ],
    }
    monkeypatch.setattr("vulnscan.scanners.subprocess.run", fake_run(payload, 1))
    report = make_scanner("semgrep", SourceWorkspace(tmp_path)).scan("a.py")
    assert report.status == "completed", report.errors
    finding = report.findings[0]
    assert finding.rule_id == "python-sql-injection"
    assert "someone" not in finding.id and finding.family == "CWE-89"
    assert normalise_semgrep_rule("python-eval-pattern") == "python-eval-pattern"


def test_bandit_reported_cwe_is_kept_but_family_uses_project_map(monkeypatch, tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x = 1\n", encoding="utf-8")
    payload = {
        "errors": [],
        "metrics": {str(path): {}, "_totals": {}},
        "results": [
            {
                "filename": str(path),
                "test_id": "B307",
                "line_number": 1,
                "issue_severity": "MEDIUM",
                "issue_confidence": "HIGH",
                "issue_text": "eval",
                "issue_cwe": {"id": 78},
            }
        ],
    }
    monkeypatch.setattr("vulnscan.scanners.subprocess.run", fake_run(payload, 1))
    finding = make_scanner("bandit", SourceWorkspace(tmp_path)).scan("a.py").findings[0]
    assert finding.cwe == "CWE-78" and finding.family == "CWE-95"
    assert set(BANDIT_FAMILY.values()) == {"CWE-95", "CWE-78", "CWE-89"}


@pytest.mark.parametrize(
    "source,rule,family",
    [
        ("import os\n\n\ndef f(name):\n    os.system('ls ' + name)\n", "B605", "CWE-78"),
        ("def f(code):\n    exec(code)\n", "B102", "CWE-95"),
        ("import subprocess\n", "B404", None),
    ],
)
def test_full_bandit_profile(tmp_path, source, rule, family):
    (tmp_path / "s.py").write_text(source, encoding="utf-8")
    report = make_scanner("bandit", SourceWorkspace(tmp_path), "full").scan("s.py")
    assert report.status == "completed", report.errors
    matching = [f for f in report.findings if f.rule_id == rule]
    assert matching, [f.rule_id for f in report.findings]
    assert matching[0].family == family


TAINT_CASES = [
    ("def f(x):\n    return eval(x)\n", "CWE-95", 1),
    ("def f(name: str):\n    return eval(name)\n", "CWE-95", 1),
    ("def f():\n    return eval('1 + 2')\n", "CWE-95", 0),
    ("import ast\n\n\ndef f(x):\n    return eval(repr(ast.literal_eval(x)))\n", "CWE-95", 0),
    ("import os\n\n\ndef f(name):\n    os.system('ls ' + name)\n", "CWE-78", 1),
    (
        (
            "import subprocess\n\n\ndef f(name):\n"
            "    return subprocess.run(f'echo {name}', shell=True)\n"
        ),
        "CWE-78",
        1,
    ),
    (
        (
            "import shlex\nimport subprocess\n\n\ndef f(name):\n"
            "    return subprocess.run('echo ' + shlex.quote(name), shell=True)\n"
        ),
        "CWE-78",
        0,
    ),
    (
        "import subprocess\n\n\ndef f(name):\n    return subprocess.run(['echo', name])\n",
        "CWE-78",
        0,
    ),
    (
        "def f(cur, name):\n    return cur.execute(f\"SELECT n FROM t WHERE n = '{name}'\")\n",
        "CWE-89",
        1,
    ),
    (
        "def f(cur, name):\n    q = 'SELECT n FROM t WHERE n = ' + name\n    return cur.execute(q)\n",
        "CWE-89",
        1,
    ),
    (
        "def f(cur, name):\n    return cur.execute('SELECT n FROM t WHERE n = ?', (name,))\n",
        "CWE-89",
        0,
    ),
    (
        (
            "def f(cur, value):\n    number = int(value)\n"
            "    return cur.execute(f'SELECT n FROM t WHERE id = {number}')\n"
        ),
        "CWE-89",
        0,
    ),
]


@pytest.mark.parametrize("source,family,expected", TAINT_CASES)
def test_semgrep_taint_rules(tmp_path, source, family, expected):
    (tmp_path / "s.py").write_text(source, encoding="utf-8")
    report = make_scanner("semgrep", SourceWorkspace(tmp_path), "full").scan("s.py")
    assert report.status == "completed", report.errors
    in_family = [f for f in report.findings if f.family == family]
    assert len(in_family) == expected, [(f.rule_id, f.line) for f in report.findings]
    assert all(not f.rule_id.count(".") for f in report.findings)


def test_workspace_collects_directories_safely(tmp_path):
    (tmp_path / "pkg" / "sub").mkdir(parents=True)
    (tmp_path / "pkg" / ".hidden").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "pkg" / "sub" / "b.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "pkg" / ".hidden" / "c.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "pkg" / "notes.txt").write_text("x\n", encoding="utf-8")
    (tmp_path / "empty").mkdir()
    workspace = SourceWorkspace(tmp_path)
    assert workspace.collect("pkg") == ["pkg/a.py", "pkg/sub/b.py"]
    assert workspace.collect("pkg/a.py") == ["pkg/a.py"]
    with pytest.raises(TargetNotFound):
        workspace.collect("missing")
    with pytest.raises(TargetNotFound):
        workspace.collect("empty")
    with pytest.raises(TargetError):
        SourceWorkspace(tmp_path, max_files=1).collect("pkg")
    with pytest.raises(TargetError):
        workspace.collect("../pkg")


def test_workspace_refuses_links_leaving_the_root(tmp_path):
    outside = tmp_path / "outside"
    root = tmp_path / "root"
    outside.mkdir()
    (root / "pkg").mkdir(parents=True)
    (outside / "secret.py").write_text("pass\n", encoding="utf-8")
    try:
        os.symlink(outside / "secret.py", root / "pkg" / "link.py")
    except OSError:
        pytest.skip("symbolic links are not permitted for this user")
    with pytest.raises(TargetError):
        SourceWorkspace(root).collect("pkg")
