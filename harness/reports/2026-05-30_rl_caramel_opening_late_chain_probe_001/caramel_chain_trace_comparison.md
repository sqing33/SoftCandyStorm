# Policy Episode Trace Comparison

- Decision: `policy_episode_trace_comparison_recorded`
- Trace groups: `caramel_chain`
- Target seed: `63402`
- Trace count: `3`

## Matched Seeds

| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |
|---:|---|---|---:|---|---|---|---|
| 63400 | `caramel_chain` | `defeat` | 213.2166 | 7:35.81%, 3:23.72%, 5:13.95%, 1:12.09%, 4:5.12% | 39.9997s a7 | 45.9996s a4 | 5:0.7553, 6:0.1432, 4:0.0747 |
| 63401 | `caramel_chain` | `defeat` | 235.3546 | 7:27.85%, 5:15.61%, 1:14.35%, 3:12.66%, 2:12.24% | 25.0s a2 | 232.0206s a5 | 2:0.8536, 3:0.071, 1:0.067 |
| 63402 | `caramel_chain` | `defeat` | 245.2901 | 7:21.86%, 5:19.84%, 3:19.43%, 8:13.77%, 1:10.12% | n/a | 239.0221s a8 | 3:0.6579, 2:0.2627, 4:0.0406 |

## Target Seed Vs Success Average

| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |
|---|---|---|---|
| `caramel_chain` | `none` | `1,3,5,7,8` | `{"1": 0.1012, "2": 0.0567, "3": 0.1943, "4": 0.085, "5": 0.1984, "7": 0.2186, "8": 0.1377}` |

## Limitations

- This report compares sampled policy traces only; unsampled frames are not inspected.
- Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.
- Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.
