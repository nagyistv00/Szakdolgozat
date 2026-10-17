# Thesis vulnerability assistant — research workspace

Author: Nagy István. Supervisor: Girászi Tamás.

Current stage: milestone 2 completed provisionally. Direction: static source analysis with a pretrained model, no model training. Python is the working target language. Scanner/model connectors and development material exist; the end-user assistant and thesis manuscript do not yet exist. Supervisor feedback, as reported by the user on 2026-10-17, accepts the pretrained-model approach without training, Python with the three weakness families, and the scanner vs. scanner + AI comparison using accuracy, precision and recall; see `RESEARCH_LOG.md`.

## Project records

- [AGENTS.md](AGENTS.md): requirements and working instructions.
- [RESEARCH_LOG.md](RESEARCH_LOG.md): dated decisions and evidence.
- [Milestone 1 notes](research/MILESTONE_1.md): research synthesis, technology comparison, findings and open decisions.
- [Source register](research/SOURCES.md): precise references, reading depth and source-specific notes.
- [Milestone 2 design and results](research/MILESTONE_2.md): component boundaries, verified connections and remaining work.
- [Supervisor discussion brief](research/SUPERVISOR_BRIEF.md): concise Hungarian meeting preparation.

## Reproduce the Windows environment

Prerequisites: uv and CPython 3.11.13. The project pins this interpreter in `.python-version`; uv may download it on a machine where it is missing. Package installation requires internet access. No paid service or API key is used by these checks.

From the project folder in PowerShell:

```powershell
uv sync --locked
uv pip check
uv run --locked ruff check src tests scripts
uv run --locked pytest -q -s --junitxml=artifacts/m2/latest-pytest.xml
```

No virtual-environment activation or machine-wide Python changes are needed. `uv.lock` records exact dependencies; preserve it when reproducing results. `pyproject.toml` records direct dependency ranges, not the exact resolved environment.

The suite currently has 40 checks. It includes the six original M1 scanner-installation checks, whose evidence remains under `artifacts/m1/<UTC timestamp>/`, plus M2 connector/error-boundary tests. The XML summary is replaced by the next run. Historical results are retained in timestamped evidence directories.

The fixture containing `eval` is intentionally unsafe source text for static analysis. Do not use it as application code. The tests do not import or execute fixture files.

These tests check installations and connector behaviour, including failures. They do not establish general vulnerability detection accuracy or AI assessment quality.

## Reproduce milestone 2 scanner diagnostics

```powershell
uv run --locked python scripts/m2_diagnostic.py
```

This scans the 18 development files with both adapters and saves raw/normalised outputs, commands, input hashes and versions under `artifacts/m2/<UTC timestamp>/`. It does not execute the samples. The three selected Bandit checks and three local Semgrep rules are deliberately limited; they are not the tools' complete rule sets.

## Optional real local model connection

The verified setup uses Windows x64, Ollama 0.34.2 and `qwen2.5-coder:7b` (Q4_K_M). Downloading requires several GB of network transfer and disk space. The existing installation and model are already present on this machine; repeat setup/pull only when provisioning or intentionally restoring them.

```powershell
# Provision on a fresh machine:
./scripts/setup_ollama.ps1
./scripts/model_server.ps1 -Action Start
uv run --locked python scripts/pull_model.py

# For an existing installation, start the server and run the diagnostic:
uv run --locked python scripts/m2_diagnostic.py --with-model
./scripts/model_server.ps1 -Action Stop
```

For an ordinary repeat run, use Start, the diagnostic, then Stop; omit setup/pull. The hidden server binds only to `127.0.0.1:11435`, with cloud features disabled. The project scripts do not install a Windows service or change PATH. Runtime binaries are under `.tools/`, model weights under `models/ollama/`, and transient server logs under `.runtime/`. These large/local directories are excluded from Git.

The download script verifies the release archive hash before extraction. If a download is interrupted and the retained archive fails its checksum, replace that exact incomplete archive before retrying; it is never executed on checksum failure. Model tags can move: compare the API digest with the recorded value in the M2 report. The package lock does not pin model weights.

The real-model diagnostic only acknowledges scanner evidence through a strict schema. It does not yet interpret a user's request, judge vulnerability correctness or produce an end-user explanation. API responses, model identity and timing are preserved with the run. The model is unloaded after the call; Stop terminates only the recorded project server after checking its identity.

## Next stage

Milestone 3 (pending the user's authorisation) will implement the natural-language workflow and evidence-backed explanations. Milestone 4 will evaluate the system on new, separately reviewed data. All current examples are development data. The thesis document will be assembled only after all four milestones.
