# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `base, branch`
- Target seed: `63402`
- Trace count: `6`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63400 | `base` | `defeat` | 214.6502 | 8:24.20%, 1:20.02%, 3:19.24%, 7:17.22%, 5:10.40% | 41.833s a7 | 213.5166s a3 | 3:0.7771, 2:0.1401, 4:0.0477 |
| 63400 | `branch` | `defeat` | 214.6502 | 8:24.20%, 1:20.02%, 3:19.24%, 7:17.22%, 5:10.40% | 41.833s a7 | 213.5166s a3 | 3:0.7771, 2:0.1401, 4:0.0477 |
| 63401 | `base` | `defeat` | 212.3497 | 7:20.94%, 3:17.73%, 8:15.53%, 1:14.82%, 2:12.16% | 24.3333s a2 | 212.0163s a3 | 3:0.7117, 4:0.127, 2:0.0858 |
| 63401 | `branch` | `defeat` | 221.1183 | 5:56.93%, 2:23.42%, 7:15.14%, 8:3.77%, 4:0.60% | 53.9995s a2 | 220.3514s a5 | 5:0.6527, 6:0.1869, 4:0.1181 |
| 63402 | `base` | `defeat` | 40.0997 | 5:69.01%, 2:16.12%, 4:14.88% | 33.4998s a5 | 39.3331s a5 | 5:0.7418, 6:0.1474, 4:0.0722 |
| 63402 | `branch` | `defeat` | 212.0497 | 5:28.96%, 2:23.78%, 7:23.39%, 1:9.26%, 4:8.16% | 51.6662s a7 | 211.8496s a5 | 5:0.6051, 4:0.2243, 6:0.0936 |

## Target Seed Vs Success Average

| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |
|---|---|---|---|
| `base` | `none` | `2,4,5` | `{"2": 0.1612, "4": 0.1488, "5": 0.6901}` |
| `branch` | `none` | `2,5,7` | `{"1": 0.0926, "2": 0.2378, "4": 0.0816, "5": 0.2896, "7": 0.2339, "8": 0.0644}` |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
