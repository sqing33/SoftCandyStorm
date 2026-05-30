# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `chained`
- Target seed: `None`
- Trace count: `3`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63400 | `chained` | `defeat` | 213.2166 | 7:35.81%, 3:23.72%, 5:13.95%, 1:12.09%, 4:5.12% | 39.9997s a7 | 45.9996s a4 | 5:0.7553, 6:0.1432, 4:0.0747 |
| 63401 | `chained` | `defeat` | 235.3546 | 7:27.85%, 5:15.61%, 1:14.35%, 3:12.66%, 2:12.24% | 25.0s a2 | 232.0206s a5 | 2:0.8536, 3:0.071, 1:0.067 |
| 63402 | `chained` | `defeat` | 41.333 | 5:60.47%, 2:16.28%, 4:16.28%, 3:6.98% | 34.9998s a5 | 40.9997s a5 | 5:0.7583, 6:0.1265, 4:0.0782 |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
