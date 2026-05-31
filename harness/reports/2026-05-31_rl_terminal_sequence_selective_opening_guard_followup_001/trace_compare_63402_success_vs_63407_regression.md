# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `regression_63407, success_63402`
- Target seed: `None`
- Trace count: `2`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63402 | `success_63402` | `victory` | 300.015 | 7:29.24%, 3:22.59%, 5:17.28%, 1:12.96%, 4:6.31% | n/a | n/a | 8:0.652, 1:0.1294, 7:0.1046 |
| 63407 | `regression_63407` | `defeat` | 231.0204 | 7:28.88%, 3:17.24%, 2:15.09%, 1:11.21%, 5:11.21% | n/a | 226.0193s a6 | 8:0.7951, 7:0.1052, 1:0.0731 |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
