# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `guard_retention_probe, parent, seed_replay_candidate`
- Target seed: `63402`
- Trace count: `9`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63400 | `guard_retention_probe` | `victory` | 60.0328 | 7:54.40%, 3:28.57%, 2:17.03% | 39.9997s a7 | n/a | 3:0.6433, 4:0.2174, 5:0.0699 |
| 63400 | `parent` | `victory` | 60.0328 | 7:54.40%, 3:28.57%, 2:17.03% | 39.9997s a7 | n/a | 3:0.6437, 4:0.2191, 5:0.0703 |
| 63400 | `seed_replay_candidate` | `victory` | 60.0328 | 7:54.40%, 3:28.57%, 2:17.03% | 39.9997s a7 | n/a | 3:0.6475, 4:0.2162, 5:0.0694 |
| 63401 | `guard_retention_probe` | `victory` | 60.0328 | 7:59.34%, 2:38.46%, 3:2.20% | 18.0001s a2 | n/a | 3:0.6298, 4:0.183, 5:0.0714 |
| 63401 | `parent` | `victory` | 60.0328 | 7:59.34%, 2:38.46%, 3:2.20% | 18.0001s a2 | n/a | 3:0.6309, 4:0.1857, 5:0.0724 |
| 63401 | `seed_replay_candidate` | `victory` | 60.0328 | 7:59.34%, 2:38.46%, 3:2.20% | 18.0001s a2 | n/a | 3:0.6342, 4:0.1829, 5:0.0714 |
| 63402 | `guard_retention_probe` | `defeat` | 37.4998 | 5:70.18%, 2:18.42%, 4:11.40% | 32.3332s a5 | 37.3331s a5 | 5:0.7706, 6:0.1347, 4:0.06 |
| 63402 | `parent` | `defeat` | 37.3331 | 5:69.91%, 2:18.58%, 4:11.50% | 31.9999s a5 | 36.9998s a5 | 5:0.7834, 6:0.1239, 4:0.0586 |
| 63402 | `seed_replay_candidate` | `defeat` | 37.2664 | 5:69.91%, 2:18.58%, 4:11.50% | 31.9999s a5 | 36.9998s a5 | 5:0.7808, 6:0.1253, 4:0.0587 |

## Target Seed Vs Success Average

| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |
|---|---|---|---|
| `guard_retention_probe` | `3,7` | `4,5` | `{"2": -0.0932, "3": -0.1539, "4": 0.114, "5": 0.7018, "7": -0.5687}` |
| `parent` | `3,7` | `4,5` | `{"2": -0.0916, "3": -0.1539, "4": 0.115, "5": 0.6991, "7": -0.5687}` |
| `seed_replay_candidate` | `3,7` | `4,5` | `{"2": -0.0916, "3": -0.1539, "4": 0.115, "5": 0.6991, "7": -0.5687}` |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
