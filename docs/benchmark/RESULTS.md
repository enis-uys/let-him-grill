# Benchmark results

Run date: 2026-07-23  
Repository revision: `dbf8381c726f845f332927ad54632fbbe3fea84a`

Five fixed scenarios were each run in a fresh Codex task with the conventional
question-by-question workflow and with Let Him Grill in compact mode. No run was
retried or excluded.

| Scenario | Baseline questions | Grill questions | Baseline seconds | Grill seconds |
| --- | ---: | ---: | ---: | ---: |
| [01](runs/01-baseline.md) / [Grill](runs/01-let-him-grill.md) | 15 | 0 | 505 | 54 |
| [02](runs/02-baseline.md) / [Grill](runs/02-let-him-grill.md) | 18 | 0 | 479 | 61 |
| [03](runs/03-baseline.md) / [Grill](runs/03-let-him-grill.md) | 6 | 0 | 190 | 46 |
| [04](runs/04-baseline.md) / [Grill](runs/04-let-him-grill.md) | 9 | 1 | 272 | 66 |
| [05](runs/05-baseline.md) / [Grill](runs/05-let-him-grill.md) | 18 | 0 | 455 | 50 |
| **Total / median** | **66** | **1** | **455 median** | **54 median** |

Elapsed ranges were 190–505 seconds for the baseline and 46–66 seconds for Let
Him Grill. The runs reported 22 versus 26 autonomous decisions respectively.
Final plans contained 9 versus 7 normalized material human gates; this was
normalized from the plan contents because baseline agents sometimes counted
every question as a gate. Raw self-reported reassessment counts were 22 versus
3, but the baseline count is not comparable: scenario 05 counted every answer
as a reassessment.

The defensible result is therefore limited to observed interruptions and time:
across these five paired tasks, Let Him Grill reduced individual questions from
66 to 1 and median time to a usable plan from 455 to 54 seconds.

Timing includes Codex execution and benchmark-controller response latency. All
tasks used the configured default model, whose model ID was not exposed by the
thread API. Treat this as reproducible product evidence, not a controlled model
performance benchmark.
