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
| union+qwen2.5-coder:7b#r1 | 6 | 10 | 2 | 0 | 0.4444 | 0.375 | 1.0 |
| model-accepted:union+qwen2.5-coder:7b#r1 | 6 | 10 | 2 | 0 | 0.4444 | 0.375 | 1.0 |
| union+qwen2.5-coder:7b#r2 | 6 | 10 | 2 | 0 | 0.4444 | 0.375 | 1.0 |
| model-accepted:union+qwen2.5-coder:7b#r2 | 6 | 10 | 2 | 0 | 0.4444 | 0.375 | 1.0 |
| semgrep+qwen2.5-coder:7b#r1 | 6 | 8 | 4 | 0 | 0.5556 | 0.4286 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:7b#r1 | 5 | 8 | 4 | 1 | 0.5 | 0.3846 | 0.8333 |
| semgrep+qwen2.5-coder:7b#r2 | 6 | 8 | 4 | 0 | 0.5556 | 0.4286 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:7b#r2 | 5 | 8 | 4 | 1 | 0.5 | 0.3846 | 0.8333 |
| union+qwen2.5-coder:7b-noverify | 6 | 10 | 2 | 0 | 0.4444 | 0.375 | 1.0 |
| union+qwen2.5-coder:14b#r1 | 6 | 7 | 5 | 0 | 0.6111 | 0.4615 | 1.0 |
| model-accepted:union+qwen2.5-coder:14b#r1 | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| union+qwen2.5-coder:14b#r2 | 6 | 7 | 5 | 0 | 0.6111 | 0.4615 | 1.0 |
| model-accepted:union+qwen2.5-coder:14b#r2 | 6 | 6 | 6 | 0 | 0.6667 | 0.5 | 1.0 |
| semgrep+qwen2.5-coder:14b#r1 | 6 | 4 | 8 | 0 | 0.7778 | 0.6 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:14b#r1 | 6 | 4 | 8 | 0 | 0.7778 | 0.6 | 1.0 |
| semgrep+qwen2.5-coder:14b#r2 | 6 | 4 | 8 | 0 | 0.7778 | 0.6 | 1.0 |
| model-accepted:semgrep+qwen2.5-coder:14b#r2 | 6 | 4 | 8 | 0 | 0.7778 | 0.6 | 1.0 |
| union+qwen2.5-coder:14b-noverify | 6 | 7 | 5 | 0 | 0.6111 | 0.4615 | 1.0 |

Model statistics: see metrics.json.
