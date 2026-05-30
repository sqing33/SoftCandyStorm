# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `candidate, parent`
- Target seed: `63402`
- Trace count: `6`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63400 | `candidate` | `victory` | 60.0328 | 7:54.40%, 3:28.57%, 2:17.03% | 39.9997s a7 | n/a | 3:0.6475, 4:0.2162, 5:0.0694 |
| 63400 | `parent` | `victory` | 60.0328 | 7:54.40%, 3:28.57%, 2:17.03% | 39.9997s a7 | n/a | 3:0.6437, 4:0.2191, 5:0.0703 |
| 63401 | `candidate` | `victory` | 60.0328 | 7:59.34%, 2:38.46%, 3:2.20% | 18.0001s a2 | n/a | 3:0.6342, 4:0.1829, 5:0.0714 |
| 63401 | `parent` | `victory` | 60.0328 | 7:59.34%, 2:38.46%, 3:2.20% | 18.0001s a2 | n/a | 3:0.6309, 4:0.1857, 5:0.0724 |
| 63402 | `candidate` | `defeat` | 37.2664 | 5:69.91%, 2:18.58%, 4:11.50% | 31.9999s a5 | 36.9998s a5 | 5:0.7808, 6:0.1253, 4:0.0587 |
| 63402 | `parent` | `defeat` | 37.3331 | 5:69.91%, 2:18.58%, 4:11.50% | 31.9999s a5 | 36.9998s a5 | 5:0.7834, 6:0.1239, 4:0.0586 |

## Target Seed Vs Success Average

| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |
|---|---|---|---|
| `candidate` | `3,7` | `4,5` | `{"2": -0.0916, "3": -0.1539, "4": 0.115, "5": 0.6991, "7": -0.5687}` |
| `parent` | `3,7` | `4,5` | `{"2": -0.0916, "3": -0.1539, "4": 0.115, "5": 0.6991, "7": -0.5687}` |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
