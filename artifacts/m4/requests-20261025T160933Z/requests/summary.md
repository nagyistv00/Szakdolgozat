# M4 held-out request evaluation

Requests: 14 (TestData/m4_requests.json). Interpreters frozen at M3.

| Interpreter | Action correct | All checks passed | Model failures | Failed IDs |
|---|---|---|---|---|
| rules | 9/14 | 9/14 | 0 | H-01, H-03, H-06, H-11, H-12 |
| model:qwen2.5-coder:14b | 13/14 | 13/14 | 0 | H-11 |
| model:qwen2.5-coder:7b | 13/14 | 13/14 | 0 | H-11 |
