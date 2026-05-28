# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 8
- Sampled rows: 2359
- Negative route_recovery rows: 1724 (73.08%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 63102 | 8.5 | `opening_lt_60` | 2 | -0.0025 | `boundary_edge` | 0.0 | caramel-slime d=517.1012 | 2:0.6766, 3:0.122, 4:0.0979 |
| `soda-creek` | 63100 | 9.0 | `opening_lt_60` | 2 | -0.0025 | `boundary_edge` | 0.0 | soda-bubble d=20.8218 | 2:0.5857, 4:0.1533, 3:0.1483 |
| `cracked-star-jar` | 63100 | 9.5 | `opening_lt_60` | 2 | -0.0025 | `boundary_edge` | 0.0 | cotton-candy-clump d=41.1151 | 2:0.6581, 3:0.1245, 4:0.1145 |
| `soda-creek` | 63101 | 45.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge` | 0.0 | soda-bubble d=839.3386 | 7:0.9576, 8:0.0151, 6:0.0117 |
| `soda-creek` | 63101 | 47.4996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=499.2747 | 7:0.9577, 8:0.0151, 6:0.0116 |
| `soda-creek` | 63101 | 47.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=469.275 | 7:0.9614, 8:0.0133, 6:0.0114 |
| `soda-creek` | 63101 | 48.4996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=439.2755 | 7:0.9614, 8:0.0133, 6:0.0114 |
| `soda-creek` | 63101 | 48.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=409.276 | 7:0.9622, 8:0.013, 6:0.0113 |
| `soda-creek` | 63101 | 49.4996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=379.2765 | 7:0.9622, 8:0.0129, 6:0.0113 |
| `soda-creek` | 63101 | 49.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=459.165 | 7:0.9589, 8:0.0147, 6:0.0115 |
| `soda-creek` | 63101 | 50.4996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=429.165 | 7:0.9602, 8:0.014, 6:0.0114 |
| `soda-creek` | 63101 | 50.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=399.165 | 7:0.96, 8:0.0141, 6:0.0114 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 783 | -0.0025 | -0.0018 | `{"2": 143, "3": 526, "5": 4, "6": 5, "7": 80, "8": 25}` |
| `cracked-star-jar` | 417 | -0.0025 | -0.0017 | `{"2": 89, "3": 45, "4": 22, "5": 43, "7": 49, "8": 169}` |
| `soda-creek` | 524 | -0.0025 | -0.0018 | `{"2": 102, "3": 45, "4": 44, "5": 37, "6": 25, "7": 85, "8": 186}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 253 | -0.0023 | -0.0019 | `{"3": 135, "5": 30, "7": 5, "8": 83}` |
| `mid_60_to_180` | 865 | -0.0025 | -0.0019 | `{"3": 481, "5": 54, "6": 30, "7": 3, "8": 297}` |
| `opening_lt_60` | 606 | -0.0025 | -0.0016 | `{"2": 334, "4": 66, "7": 206}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boss_pressure` | 2 | -0.0006 | -0.0004 | `{"8": 2}` |
| `boundary_edge` | 1663 | -0.0025 | -0.0018 | `{"2": 313, "3": 608, "4": 61, "5": 83, "6": 25, "7": 212, "8": 361}` |
| `enemy_pressure` | 41 | -0.0022 | -0.0011 | `{"2": 40, "8": 1}` |
| `hazard_pressure` | 82 | -0.0023 | -0.0016 | `{"2": 34, "3": 13, "5": 7, "6": 1, "7": 22, "8": 5}` |
| `low_health` | 181 | -0.0025 | -0.0021 | `{"2": 2, "3": 3, "4": 7, "5": 33, "7": 52, "8": 84}` |
| `no_major_pressure` | 57 | -0.0018 | -0.0006 | `{"2": 21, "3": 8, "4": 5, "5": 1, "6": 5, "7": 2, "8": 15}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
