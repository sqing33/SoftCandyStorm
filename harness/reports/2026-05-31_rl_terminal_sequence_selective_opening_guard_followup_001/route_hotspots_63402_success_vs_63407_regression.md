# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 2
- Sampled rows: 533
- Negative route_recovery rows: 140 (26.27%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 63407 | 8.0 | `opening_lt_60` | 2 | -0.0101 | `boundary_edge` | 0.0 | caramel-slime d=92.769 | 2:0.5313, 3:0.1584, 1:0.1062 |
| `caramel-workshop` | 63407 | 11.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=410.5035 | 2:0.4668, 1:0.19, 3:0.1058 |
| `caramel-workshop` | 63407 | 12.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=0.0 | 2:0.5382, 1:0.2202, 3:0.0784 |
| `caramel-workshop` | 63407 | 13.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | bouncy-gummy d=0.0 | 2:0.4954, 1:0.2548, 3:0.0728 |
| `caramel-workshop` | 63407 | 14.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=180.6063 | 2:0.4802, 1:0.2542, 3:0.0723 |
| `caramel-workshop` | 63407 | 15.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=135.6063 | 2:0.5067, 1:0.2199, 3:0.0867 |
| `caramel-workshop` | 63407 | 16.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=185.5035 | 2:0.5484, 3:0.136, 1:0.1225 |
| `caramel-workshop` | 63407 | 17.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=143.6724 | 2:0.5513, 3:0.1743, 4:0.0957 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 140 | -0.0101 | -0.0042 | `{"1": 9, "2": 24, "3": 16, "4": 7, "5": 29, "6": 1, "7": 44, "8": 10}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 20 | -0.0015 | -0.0007 | `{"1": 2, "3": 7, "4": 1, "5": 3, "7": 6, "8": 1}` |
| `mid_60_to_180` | 40 | -0.0017 | -0.0008 | `{"1": 7, "3": 9, "4": 1, "5": 7, "6": 1, "7": 9, "8": 6}` |
| `opening_lt_60` | 79 | -0.0101 | -0.0069 | `{"2": 24, "4": 5, "5": 19, "7": 29, "8": 2}` |
| `post_300` | 1 | -0.0001 | -0.0001 | `{"8": 1}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 104 | -0.0101 | -0.0054 | `{"1": 3, "2": 22, "3": 6, "4": 5, "5": 24, "7": 39, "8": 5}` |
| `hazard_pressure` | 5 | -0.01 | -0.009 | `{"2": 5}` |
| `no_major_pressure` | 36 | -0.0039 | -0.001 | `{"1": 6, "2": 2, "3": 10, "4": 2, "5": 5, "6": 1, "7": 5, "8": 5}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
