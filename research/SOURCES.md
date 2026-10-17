# Milestone 1 source register

Access date for every entry: **2026-09-19**. This is a research record, not the final thesis bibliography. Notes are paraphrases. Reading depth is explicit; no experiment from a cited paper has been reproduced here. Live documentation must be checked again when implementing the selected component.

## Research papers and benchmark documentation

### R01 — Devign: graph-based learning

- Authors: Yaqin Zhou, Shangqing Liu, Jingkai Siow, Xiaoning Du, Yang Liu.
- Title: *Devign: Effective Vulnerability Identification by Learning Comprehensive Program Semantics via Graph Neural Networks*.
- Year/version: 2019, arXiv:1909.03496.
- Primary source: https://arxiv.org/abs/1909.03496
- Reading depth: abstract and bibliographic metadata.
- Source claim: graph neural networks learn from structural and semantic representations of code to classify functions; the study uses four C projects.
- Project interpretation: a useful representative of supervised graph approaches. Reproducing it would require graph extraction and labelled data, a different commitment from adding a natural-language interface to existing scanners.
- Limitation of this review: training details and the full experimental protocol have not yet been inspected. Reported performance must not be transferred to our project.

### R02 — CodeBERT: code and natural-language representations

- Authors: Zhangyin Feng, Daya Guo, Duyu Tang, Nan Duan, Xiaocheng Feng, Ming Gong, Linjun Shou, Bing Qin, Ting Liu, Daxin Jiang, Ming Zhou.
- Title: *CodeBERT: A Pre-Trained Model for Programming and Natural Languages*.
- Publication: Findings of EMNLP 2020, pp. 1536–1547, Association for Computational Linguistics.
- DOI: 10.18653/v1/2020.findings-emnlp.139
- Primary source: https://aclanthology.org/2020.findings-emnlp.139/
- Reading depth: abstract and publisher metadata.
- Source claim: joint code/natural-language pretraining supports code search and documentation generation.
- Project interpretation: relevant background for learned code representations. The cited evaluation is not proof of vulnerability detection accuracy and does not make CodeBERT a ready-made conversational security assistant.

### R03 — Hungarian research: process metrics

- Authors: Tamás Viszkok, Péter Hegedűs, Rudolf Ferenc.
- Title: *Improving Vulnerability Prediction of JavaScript Functions Using Process Metrics*.
- Version: arXiv:2105.07527v1, 2021-05-16.
- DOI for the consulted preprint: 10.48550/arXiv.2105.07527
- Primary source: https://arxiv.org/abs/2105.07527
- Consulted full-text sections: https://arxiv.org/html/2105.07527v1 — results, section 5 (Threats to Validity), section 6 (Conclusion), author affiliations.
- Source claim: adding process metrics from development history improves prediction in their JavaScript dataset. The authors discuss the small dataset and class imbalance as limitations.
- Project interpretation: this University of Szeged-affiliated study provides a directly relevant Hungarian research contribution, written in English. It supports considering a classical ML baseline if model training becomes part of the scope.
- Caution: process-history information must be restricted to what existed at the analysed revision. A study on JavaScript functions is not a measured result on our Python smoke fixtures.

### R04 — PrimeVul: evaluation validity

- Authors: Yangruibo Ding, Yanjun Fu, Omniyyah Ibrahim, Chawin Sitawarin, Xinyun Chen, Basel Alomair, David Wagner, Baishakhi Ray, Yizheng Chen.
- Title: *Vulnerability Detection with Code Language Models: How Far Are We?*
- Consulted version: arXiv:2403.18624v2, 2024-07-10; landing page notes ICSE 2025 acceptance. Use the consulted preprint version until final publication metadata is checked.
- DOI: 10.48550/arXiv.2403.18624
- Primary source: https://arxiv.org/abs/2403.18624
- Consulted full-text sections: https://arxiv.org/html/2403.18624v2 — introduction/evaluation guidelines and section II-B on label inspection.
- Source claim: dataset label errors, duplicates and evaluation choices can inflate apparent detection quality. The work proposes chronological splitting, deduplication and vulnerable/fixed pair evaluation.
- Project interpretation: keep development examples separate from final evaluation data; check labels and report false positives. A security-fix commit does not prove that every modified function was vulnerable.
- Applicability limit: the inspected benchmark discussion concerns C/C++ functions; it is methodological background, not a ready-made Python benchmark.

### R05 — IRIS: LLM-assisted static analysis

- Authors: Ziyang Li, Saikat Dutta, Mayur Naik.
- Title: *IRIS: LLM-Assisted Static Analysis for Detecting Security Vulnerabilities*.
- Consulted version: arXiv:2405.17238v3, 2025-04-06.
- DOI: 10.48550/arXiv.2405.17238
- Primary source: https://arxiv.org/abs/2405.17238
- Consulted full-text sections: https://arxiv.org/html/2405.17238v3 — framework overview, dataset/evaluation setup and section 7 (Conclusion and Limitations).
- Source claim: IRIS combines LLM-derived taint specifications and contextual alert assessment with static analysis. Its evaluation uses real Java projects; the authors identify model-call cost, missed vulnerabilities and uncertain transfer to other languages as limitations.
- Project interpretation: a hybrid approach is a defensible research direction. Merely summarising scanner output would not reproduce IRIS or demonstrate improved detection.
- Limitation: we have not reproduced its experiments, and its benchmark is not directly interchangeable with Python fixtures.

### R06 — Repository-level LLM/agent evaluation

- Authors: Alperen Yildiz, Sin G Teo, Yiling Lou, Yebo Feng, Chong Wang, Dinil Mon Divakaran.
- Title: *Benchmarking LLMs and LLM-based Agents in Practical Vulnerability Detection for Code Repositories*.
- Publication: ACL 2025, Volume 1: Long Papers, pp. 30848–30865.
- DOI: 10.18653/v1/2025.acl-long.1490
- Primary source: https://aclanthology.org/2025.acl-long.1490/
- Reading depth: abstract and publisher metadata.
- Source claim: JITVul links functions to introducing/fixing commits; context-aware agents improve discrimination in the reported evaluation but still produce inconsistent judgements.
- Project interpretation: test context availability and vulnerable/fixed pairs; do not infer repository-level effectiveness from isolated snippets.
- Next reading if selected: inspect full experimental design before reproducing any comparison.

### R07 — Recent work: hypothesis validation

- Authors: Ziliang Wang, Ge Li, Jia Li, Hao Zhu, Zhi Jin.
- Title: *VulAgent: Hypothesis-Validation Driven Multi-Agent Architecture for Vulnerability Detection*.
- Publication: Findings of ACL 2026, pp. 18598–18616.
- DOI: 10.18653/v1/2026.findings-acl.928
- Primary source: https://aclanthology.org/2026.findings-acl.928/
- Reading depth: abstract and publisher metadata.
- Source claim: the proposed system forms vulnerability hypotheses around sensitive operations and validates their preconditions against project context.
- Project interpretation: useful motivation for requiring evidence behind findings. This does not justify adding multiple agents to our small prototype without measuring their benefit.
- Limitation: full methodology and reported numerical comparisons remain to be critically reviewed if this approach is adopted.

### R08 — Juliet synthetic test suites

- Author: Paul E. Black.
- Title: *Juliet 1.3 Test Suite: Changes From 1.2*.
- Publication: NIST Technical Note 1995, 2018-06-14.
- DOI: 10.6028/NIST.TN.1995
- Primary source: https://www.nist.gov/publications/juliet-13-test-suite-changes-12
- Reading depth: NIST publication abstract and metadata.
- Source claim: small C/C++ and Java programs cover many weakness classes; the report also documents remaining systematic issues.
- Project interpretation: useful for controlled scanner testing if a supported language is selected. It is synthetic and cannot establish effectiveness on real repositories; it is not a Python dataset.

## Official technical references

| ID | Maintainer / title | Exact document | Inspected information and use |
| --- | --- | --- | --- |
| T01 | Bandit maintainers — Welcome to Bandit | https://bandit.readthedocs.io/en/latest/ | AST-based Python checks and reporting; Apache 2.0 notice. Candidate deterministic baseline. |
| T02 | Semgrep — Community Edition | https://semgrep.dev/products/community-edition/ | Local CLI and Windows installation, language coverage. Installation feasibility, not proof of finding quality. |
| T03 | Semgrep — source repository README | https://github.com/semgrep/semgrep | Local rules and telemetry behaviour. Local runs additionally verified against installed CLI help. |
| T04 | GitHub — CodeQL CLI | https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli | Code databases, query execution, SARIF and usage eligibility. Comparison candidate; not installed. |
| T05 | ZAP — Features | https://www.zaproxy.org/docs/desktop/start/features/ | Running web-application analysis, passive/active scanning and automation options. A separate dynamic-analysis direction; not installed or run. |
| T06 | OWASP — LLM Prompt Injection Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | Agent-specific manipulation, tool-parameter validation and least privilege. Motivation for keeping inspected content separate from execution authority. |
| T07 | Astral — Working on projects | https://docs.astral.sh/uv/guides/projects/ | Project dependencies, environment and lockfile workflow. Applied to local setup. |
| T08 | Ollama — Structured outputs | https://ollama.com/blog/structured-outputs | JSON-schema-constrained generation. Candidate local integration path; runtime/model not installed. Schema conformity alone does not establish semantic correctness. |
| T09 | Qwen — Qwen2.5-Coder-7B-Instruct model card | https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct | A representative code-oriented instruction model candidate, not a claim about the newest or best available model. No local inference performed. |

## Search and selection notes

- Search date: 2026-09-19. Sources: arXiv, ACL Anthology, NIST, Hungarian university-affiliated research and official tool documentation.
- Search themes: graph-based vulnerability detection; code/natural-language pretraining; Hungarian vulnerability prediction; dataset leakage and label quality; LLM/static-analysis hybrids; repository-level agents; Windows-compatible scanners.
- Representative queries included `Devign effective vulnerability identification graph neural networks`, `CodeBERT pre-trained model programming natural languages`, `machine learning vulnerability detection static analysis site:crysys.hu`, and `LLM assisted static analysis vulnerability detection`.
- Included sources with direct relevance to method selection, evaluation or local feasibility. Search-engine snippets were used to discover sources; core decisions use primary pages and, for R03–R05, inspected full-text sections.
- This is a scoped initial review, not an exhaustive systematic literature review. R01, R02, R06 and R07 need deeper reading if their methods enter the implementation or thesis claims.
- The Semgrep documentation entry point failed through the browsing tool; the official product page, repository information and installed CLI were used instead. The Ollama API documentation URL failed; the official structured-output article was accessible.

## Milestone 2 technical additions

Access date: 2026-09-19. These primary references informed implementation and corpus definitions. They are documentation, not independent proof of our system's detection quality.

| ID | Maintainer / document | Exact source | Applied information |
| --- | --- | --- | --- |
| T10 | Ollama — Windows | https://docs.ollama.com/windows | Standalone Windows archive and local runtime configuration. |
| T11 | Ollama — Generate a chat message | https://docs.ollama.com/api/chat | Non-streaming chat response, JSON schema format, completion status and timing fields. |
| T12 | Ollama — Structured Outputs | https://docs.ollama.com/capabilities/structured-outputs | Passing a schema and validating returned data; syntactic constraints do not prove semantic correctness. |
| T13 | Ollama — qwen2.5-coder:7b | https://ollama.com/library/qwen2.5-coder:7b | Model choice for the connector trial. Actual local quantisation, size and digest captured independently through the API. |
| T14 | Ollama official GitHub release | https://github.com/ollama/ollama/releases/tag/v0.34.2 | Versioned Windows archive; SHA-256 obtained from https://api.github.com/repos/ollama/ollama/releases/tags/v0.34.2 and checked locally. |
| T15 | MITRE — CWE-95 | https://cwe.mitre.org/data/definitions/95.html | Definition of eval injection; used to scope provisional labels. |
| T16 | MITRE — CWE-78 | https://cwe.mitre.org/data/definitions/78.html | Definition of command injection; input control matters when distinguishing controls. |
| T17 | MITRE — CWE-89 | https://cwe.mitre.org/data/definitions/89.html | Definition of SQL injection; database-bound data is distinct from query-like text. |
| T18 | Bandit — blacklist calls | https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html | B307 eval-call rule; initial guessed standalone B307 documentation URL was unavailable. |
| T19 | Bandit — B602 | https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html | Shell-using subprocess checks and their context-dependent warning severity. |
| T20 | Bandit — B608 | https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html | SQL-like string-building checks and confidence limitations. |

Ollama's previously inaccessible API documentation was accessible during M2. CLI configuration was also checked against the installed `ollama serve --help`, including `OLLAMA_NO_CLOUD`. The model's source licence text is retained in `artifacts/m2/model-install.json`; no weight training or modification was performed.
