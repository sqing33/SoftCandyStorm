# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `baseline_success_63407, candidate_regression_63407`
- Target seed: `63407`
- Trace count: `2`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63407 | `baseline_success_63407` | `victory` | 300.015 | 7:23.92%, 5:16.61%, 1:14.62%, 2:14.29%, 3:13.62% | n/a | n/a | 5:0.7811, 6:0.0984, 4:0.0841 |
| 63407 | `candidate_regression_63407` | `defeat` | 231.0204 | 7:28.88%, 3:17.24%, 2:15.09%, 1:11.21%, 5:11.21% | n/a | 226.0193s a6 | 8:0.7951, 7:0.1052, 1:0.0731 |

## Target Seed Vs Success Average

| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |
|---|---|---|---|
| `baseline_success_63407` | `none` | `1,2,3,5,7` | `{"1": 0.1462, "2": 0.1429, "3": 0.1362, "4": 0.0897, "5": 0.1661, "7": 0.2392, "8": 0.0698}` |
| `candidate_regression_63407` | `none` | `1,2,3,5,7` | `{"1": 0.1121, "2": 0.1509, "3": 0.1724, "4": 0.0733, "5": 0.1121, "7": 0.2888, "8": 0.0603}` |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
