# Milestone 1 — research and environment preparation

Date: 2026-09-19. This is an engineering/research note, not a thesis chapter.

Historical M1 snapshot: later scope decisions and the real model integration are recorded in `MILESTONE_2.md`; the open decisions below describe the state at M1 completion.

## Scope and status

The user authorised milestone 1 and accepted a local Python foundation without paid services. The final analysis target is **undecided**. Python source analysis is a reversible installation experiment, consistent with the original topic's static-analysis wording; it is not a confirmed restriction on the eventual product.

Milestone 1 delivers a scoped literature review, a comparison of candidate technologies, an isolated and locked development environment, and reproducible scanner smoke checks. Application architecture, natural-language tool control, model integration and benchmark construction belong to later milestones.

## What the initial research establishes

The inspected literature spans seven research papers and one NIST benchmark publication. Exact bibliographic details, links, reading depth and limitations are in [SOURCES.md](SOURCES.md).

| Approach | Representative source | What it would mean for this project |
| --- | --- | --- |
| Classical supervised learning | R03, Hungarian JavaScript/process-metric research | Extract features, obtain independently labelled examples, train and evaluate a classifier. Manage revision history and class imbalance. |
| Learned graph representations | R01, Devign | Build code graphs and train a graph classifier; a substantial data and representation pipeline. |
| Pretrained code representations | R02, CodeBERT | Use or fine-tune code embeddings for a specified task; not an out-of-the-box vulnerability assistant. |
| LLM-assisted static analysis | R05, IRIS | Combine model reasoning with program-analysis evidence; assess what the model adds beyond the underlying scanner. |
| Context-aware tool use / validation | R06, JITVul study; R07, VulAgent | Retrieve relevant context and check finding preconditions. More elaborate agents must justify their complexity through measurement. |
| Evaluation methodology | R04, PrimeVul; R08, Juliet | Distinguish controlled synthetic checks from realistic evaluation; check labels, duplication and vulnerable/fixed pairs. |

**Project inference:** a bounded hybrid assistant is a reasonable starting candidate for the planned title and four-milestone schedule. It can make scanner use easier and explain evidence, while a comparison with the scanner alone tests whether AI adds measurable value. This is a recommendation, not an architecture decision or an experimental result.

**Important distinction:** an LLM that only translates user requests into scanner invocations is not a newly trained vulnerability detector. An LLM that rewords existing findings has not, by that fact alone, improved detection. The claimed contribution and evaluation must match the implemented role.

## Existing solutions and candidate roles

The descriptions below are drawn from official sources T01–T09; local installation observations are explicitly identified.

| Candidate | Role | Fit and limitations | M1 action |
| --- | --- | --- | --- |
| Bandit | Python AST-based security checks | Lightweight deterministic baseline; language-specific and rule-dependent | Installed; B307 checked locally |
| Semgrep Community Edition | Pattern/rule-based static analysis | Extensible local rules and broader language coverage; selected rule coverage is not whole-program correctness | Installed; one local rule checked |
| CodeQL | Database/query-based code analysis | Candidate for richer data-flow work; setup and applicable usage terms must be considered for the chosen repository | Reviewed, not installed |
| ZAP | Dynamic web-application analysis | Relevant if the user chooses a running application; needs a local test application and a different test protocol | Reviewed, not installed or run |
| scikit-learn | Classical ML and evaluation utilities | Supports later baselines and metrics; useful without committing to a large language model | Installed; numerical import/runtime check passed |
| Ollama | Candidate local LLM runtime | Official structured-output support is relevant; structured JSON still needs semantic validation | Reviewed, not installed |
| Qwen2.5-Coder-7B-Instruct | Representative local-model candidate | Code-oriented instruction model; quality, memory use and tool-request reliability must be measured locally | Model card reviewed; weights not downloaded |

The model example is not a ranking or a claim that it is the latest/best choice. Actual model and runtime selection remains for milestone 2 after the task is fixed. No LLM inference or model training has been performed.

## Target choice still to resolve

| Option | Alignment with the submitted topic | Additional work needed |
| --- | --- | --- |
| Static source analysis with natural-language assistance | Direct match to the original static-code-analysis description | Choose target language, weakness classes and independently labelled examples |
| Analysis of a running local web application | Fits the broader cyber-defence assistant title, but changes emphasis from the original description | Confirm scope with the supervisor; prepare an isolated application and dynamic-testing protocol |
| Both | Broad coverage | Larger integration and evaluation burden; defer until a narrow path is demonstrated |

Recommendation for the next discussion: start with static source analysis, one target language and a small set of weakness classes. The implementation language being Python does **not** require the inspected code to be Python. This remains the user's choice.

The other unresolved question is whether the supervisor expects **training a model** or accepts applying a pretrained model. On 2026-09-19 the user confirmed this has not yet been discussed with the supervisor; neither answer is assumed.

## Development environment

Measured locally on 2026-09-19:

- Windows x64; Python reports Windows build 26200. The `platform` label includes Windows-10 and must not be treated as a reliable marketing edition name.
- RAM: 34,163,777,536 bytes reported by Windows.
- GPU: NVIDIA GeForce RTX 4070, 12,282 MiB reported by `nvidia-smi`; driver 616.92. No GPU inference was tested.
- WSL launcher exists but reports no installed WSL environment. Docker and Ollama were not found on PATH; this is not a claim that every possible installation location was searched.
- Several Python registrations/paths are misleadingly named. The project explicitly selects the existing uv-managed **CPython 3.11.13**, verified at runtime.
- uv 0.10.11; project environment in `.venv`; exact dependency versions in `uv.lock`.

Installed direct tools/libraries: Bandit 1.9.4, Semgrep 1.177.0, HTTPX 0.28.1, Pydantic 2.13.5, scikit-learn 1.9.1; development tools pytest 9.1.1 and Ruff 0.16.8. The resolver installed 81 packages including transitive dependencies. HTTPX/Pydantic prepare later model communication and validated data handling; no server or application is implemented.

The local setup needs no account or paid API. Scanner tests use local rules with Semgrep metrics and version checks disabled. The tests inspect source text and do not execute the intentionally unsafe fixture.

**Observed setup issues:** uv fell back from hardlinks to file copies; installation succeeded. Semgrep help emitted a formatting warning, while the tested scans completed with empty error arrays. These observations do not establish compatibility beyond this tested setup.

## Checks and evidence

- `uv pip check`: installed dependencies compatible.
- HTTPX, Pydantic and scikit-learn imports succeeded; a tiny confusion-matrix operation checked the numerical runtime. It is not an ML experiment.
- Six scanner checks: two installed analyzers × three original synthetic fixtures.
- Positive fixture: selected rule reports the direct `eval` call at line 2.
- Control fixtures: literal parsing and comment/string-only mentions produce zero selected-rule findings.
- Checks also verify expected exit codes, valid JSON, absence of scanner errors and evidence that the target was scanned. This avoids mistaking a skipped file for a clean result.
- Every test session records the tool commands, timing, raw outputs, package versions and SHA-256 hashes of fixtures/configuration under `artifacts/m1/<UTC timestamp>/`.
- `artifacts/m1/latest-pytest.xml` is the latest test summary; timestamped run directories preserve previous evidence. `artifacts/m1/environment.json` records setup observations.

The smoke fixtures are **not** a benchmark or training set. Six passing installation checks do not imply a measured detection rate, low false-positive rate on real projects, or AI effectiveness. No claim of complete security follows from an empty scanner report.

## Evaluation considerations carried forward to milestone 2

These are research-derived requirements to refine, not a completed experiment design:

- Decide the evaluation unit (finding, line, function or repository) before counting outcomes.
- Preserve the original scanner findings separately from AI-generated judgements and explanations, so changed or unsupported claims remain visible.
- Compare the scanner alone with the proposed AI-assisted system on the same held-out cases. Add a model-only comparison only if it answers a defined research question.
- Report precision, recall, F1 and false-positive rate with their counts and denominators. Keep scanner failures, model failures and abstentions explicit rather than silently treating them as safe code.
- Test vulnerable/fixed pairs and realistic negatives. Do not split near-duplicates, matching pairs or revisions from one project carelessly across development and final evaluation.
- Measure repeated-run consistency, analysis time and explanation support. A natural-language interface also needs request-understanding and invalid-request tests, separate from detection metrics.
- Treat code comments and tool output as untrusted input; later tool execution should use validated parameters and a bounded set of operations. OWASP T06 informs this requirement; no guardrail implementation exists yet.
- Log dataset provenance/licence, exact revisions, model identity, prompt/configuration versions and resource constraints when those are chosen.

## Handoff and completion boundaries

- **Completed:** initial method/technology review, source register including Hungarian research, candidate comparison, local Python/scanner/test environment, lockfile, installation verification and evidence logging.
- **Open for milestone 2:** target type and language; scope of the AI contribution; supervisor expectations about training; model/runtime; data selection; detailed architecture and evaluation protocol.
- **Not started:** product implementation, full benchmark curation, model training/inference, accuracy experiments, or thesis prose.

The environment is ready for the next design step. It is not yet an operational AI vulnerability assistant, and moving to a different target may require additional tools.
