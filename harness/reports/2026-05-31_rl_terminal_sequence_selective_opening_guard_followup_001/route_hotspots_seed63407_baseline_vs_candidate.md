# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 2
- Sampled rows: 533
- Negative route_recovery rows: 148 (27.77%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 63407 | 8.0 | `opening_lt_60` | 2 | -0.0101 | `boundary_edge` | 0.0 | caramel-slime d=92.769 | 2:0.5319, 3:0.159, 1:0.1066 |
| `caramel-workshop` | 63407 | 8.0 | `opening_lt_60` | 2 | -0.0101 | `boundary_edge` | 0.0 | caramel-slime d=92.769 | 2:0.5313, 3:0.1584, 1:0.1062 |
| `caramel-workshop` | 63407 | 11.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=410.5035 | 2:0.4664, 1:0.1898, 3:0.1059 |
| `caramel-workshop` | 63407 | 11.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=410.5035 | 2:0.4668, 1:0.19, 3:0.1058 |
| `caramel-workshop` | 63407 | 12.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=0.0 | 2:0.5396, 1:0.2197, 3:0.0781 |
| `caramel-workshop` | 63407 | 12.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=0.0 | 2:0.5382, 1:0.2202, 3:0.0784 |
| `caramel-workshop` | 63407 | 13.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | bouncy-gummy d=0.0 | 2:0.4967, 1:0.2543, 3:0.0725 |
| `caramel-workshop` | 63407 | 13.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | bouncy-gummy d=0.0 | 2:0.4954, 1:0.2548, 3:0.0728 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 148 | -0.0101 | -0.0048 | `{"1": 13, "2": 48, "3": 10, "4": 3, "5": 10, "6": 2, "7": 57, "8": 5}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 23 | -0.0016 | -0.0007 | `{"1": 5, "2": 1, "3": 2, "4": 2, "5": 2, "6": 1, "7": 6, "8": 4}` |
| `mid_60_to_180` | 37 | -0.0017 | -0.0008 | `{"1": 8, "2": 1, "3": 8, "4": 1, "5": 8, "6": 1, "7": 9, "8": 1}` |
| `opening_lt_60` | 88 | -0.0101 | -0.0075 | `{"2": 46, "7": 42}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 116 | -0.0101 | -0.0058 | `{"1": 5, "2": 44, "3": 6, "5": 7, "7": 52, "8": 2}` |
| `hazard_pressure` | 10 | -0.01 | -0.009 | `{"2": 10}` |
| `no_major_pressure` | 32 | -0.0039 | -0.0009 | `{"1": 8, "2": 4, "3": 4, "4": 3, "5": 3, "6": 2, "7": 5, "8": 3}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
