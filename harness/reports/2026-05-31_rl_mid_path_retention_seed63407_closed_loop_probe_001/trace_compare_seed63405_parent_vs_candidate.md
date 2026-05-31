# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `a_parent, b_candidate`
- Target seed: `63405`
- Trace count: `2`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63405 | `a_parent` | `defeat` | 214.5169 | 5:26.39%, 3:23.15%, 7:15.28%, 8:15.28%, 1:10.19% | 100.9988s a5 | 214.0168s a8 | 8:0.39, 1:0.2357, 4:0.1075 |
| 63405 | `b_candidate` | `defeat` | 138.6673 | 7:31.43%, 5:23.57%, 1:17.86%, 3:15.00%, 2:7.86% | 45.9996s a7 | 138.0005s a3 | 3:0.3923, 4:0.3517, 5:0.1837 |

## Target Seed Vs Success Average

| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |
|---|---|---|---|
| `a_parent` | `none` | `1,3,5,7,8` | `{"1": 0.1019, "2": 0.0509, "3": 0.2315, "5": 0.2639, "7": 0.1528, "8": 0.1528}` |
| `b_candidate` | `none` | `1,3,5,7` | `{"1": 0.1786, "2": 0.0786, "3": 0.15, "5": 0.2357, "7": 0.3143}` |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
