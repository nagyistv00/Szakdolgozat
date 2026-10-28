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
| m3:scanners+model#r1 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| model-accepted#r1 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| m3:scanners+model#r2 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| model-accepted#r2 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| m3:scanners+model#r3 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |
| model-accepted#r3 | 6 | 9 | 3 | 0 | 0.5 | 0.4 | 1.0 |

Model statistics: see metrics.json.
