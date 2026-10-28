# M3 development run (development corpus — not a final evaluation)

Cases: 18 (6 vulnerable, 12 non-vulnerable). Unit: file w.r.t. its labelled family.

| Condition | TP | FP | TN | FN | Accuracy | Precision | Recall |
|---|---|---|---|---|---|---|---|
| m2:bandit | 5 | 5 | 7 | 1 | 0.6667 | 0.5 | 0.8333 |
| m2:semgrep | 4 | 4 | 8 | 2 | 0.6667 | 0.5 | 0.6667 |
| m2:scanners | 5 | 5 | 7 | 1 | 0.6667 | 0.5 | 0.8333 |
| m3:bandit | 5 | 5 | 7 | 1 | 0.6667 | 0.5 | 0.8333 |
| m3:semgrep | 5 | 1 | 11 | 1 | 0.8889 | 0.8333 | 0.8333 |
| m3:scanners | 5 | 5 | 7 | 1 | 0.6667 | 0.5 | 0.8333 |
| union+qwen2.5-coder:14b#r1 | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| model-accepted:union+qwen2.5-coder:14b#r1 | 6 | 5 | 7 | 0 | 0.7222 | 0.5455 | 1.0 |
| union+qwen2.5-coder:14b#r2 | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| model-accepted:union+qwen2.5-coder:14b#r2 | 6 | 5 | 7 | 0 | 0.7222 | 0.5455 | 1.0 |
| semgrep+qwen2.5-coder:14b#r1 | 6 | 2 | 10 | 0 | 0.8889 | 0.75 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:14b#r1 | 6 | 2 | 10 | 0 | 0.8889 | 0.75 | 1.0 |
| semgrep+qwen2.5-coder:14b#r2 | 6 | 2 | 10 | 0 | 0.8889 | 0.75 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:14b#r2 | 6 | 2 | 10 | 0 | 0.8889 | 0.75 | 1.0 |
| union+qwen2.5-coder:14b-noverify | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| union+qwen2.5-coder:7b#r1 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| model-accepted:union+qwen2.5-coder:7b#r1 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| union+qwen2.5-coder:7b#r2 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| model-accepted:union+qwen2.5-coder:7b#r2 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| semgrep+qwen2.5-coder:7b#r1 | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:7b#r1 | 5 | 6 | 6 | 1 | 0.6111 | 0.4545 | 0.8333 |
| semgrep+qwen2.5-coder:7b#r2 | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:7b#r2 | 5 | 6 | 6 | 1 | 0.6111 | 0.4545 | 0.8333 |
| union+qwen2.5-coder:7b-noverify | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |

Model statistics: see metrics.json.
