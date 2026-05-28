# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 8
- Sampled rows: 1369
- Negative route_recovery rows: 926 (67.64%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `soda-creek` | 63100 | 9.0 | `opening_lt_60` | 2 | -0.0025 | `boundary_edge` | 0.0 | soda-bubble d=20.8218 | 2:0.5857, 4:0.1533, 3:0.1483 |
| `soda-creek` | 63101 | 45.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge` | 0.0 | soda-bubble d=839.3386 | 7:0.9576, 8:0.0151, 6:0.0117 |
| `soda-creek` | 63101 | 47.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=469.275 | 7:0.9614, 8:0.0133, 6:0.0114 |
| `soda-creek` | 63101 | 48.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=409.276 | 7:0.9622, 8:0.013, 6:0.0113 |
| `soda-creek` | 63101 | 49.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=459.165 | 7:0.9589, 8:0.0147, 6:0.0115 |
| `soda-creek` | 63101 | 50.9996 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=399.165 | 7:0.96, 8:0.0141, 6:0.0114 |
| `soda-creek` | 63100 | 51.9995 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=592.4011 | 4:0.7681, 5:0.187, 3:0.0273 |
| `soda-creek` | 63101 | 51.9995 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | soda-bubble d=419.3393 | 7:0.9586, 8:0.0149, 6:0.0115 |
| `soda-creek` | 63100 | 52.9995 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=532.4018 | 4:0.7654, 5:0.1883, 3:0.0283 |
| `soda-creek` | 63100 | 53.9995 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=323.6272 | 4:0.7352, 5:0.202, 3:0.0392 |
| `soda-creek` | 63100 | 54.9995 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge` | 0.0 | soda-bubble d=362.4439 | 4:0.7819, 5:0.1781, 3:0.0242 |
| `soda-creek` | 63101 | 54.9995 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=210.5441 | 7:0.9568, 8:0.0157, 6:0.0117 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 341 | -0.0023 | -0.0017 | `{"1": 1, "2": 81, "3": 159, "4": 3, "5": 46, "7": 37, "8": 14}` |
| `cracked-star-jar` | 239 | -0.0025 | -0.0019 | `{"2": 38, "3": 52, "4": 1, "5": 94, "7": 46, "8": 8}` |
| `soda-creek` | 346 | -0.0025 | -0.0019 | `{"1": 106, "2": 49, "3": 77, "4": 23, "5": 49, "7": 41, "8": 1}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 145 | -0.0025 | -0.0018 | `{"1": 32, "2": 9, "3": 61, "5": 36, "8": 7}` |
| `mid_60_to_180` | 475 | -0.0025 | -0.002 | `{"1": 75, "3": 227, "4": 4, "5": 153, "8": 16}` |
| `opening_lt_60` | 306 | -0.0025 | -0.0016 | `{"2": 159, "4": 23, "7": 124}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boss_pressure` | 14 | -0.0025 | -0.0019 | `{"1": 2, "3": 5, "5": 7}` |
| `boundary_edge` | 885 | -0.0025 | -0.0019 | `{"1": 102, "2": 158, "3": 279, "4": 25, "5": 185, "7": 123, "8": 13}` |
| `enemy_pressure` | 27 | -0.0024 | -0.0011 | `{"2": 22, "3": 3, "5": 1, "7": 1}` |
| `hazard_pressure` | 47 | -0.0024 | -0.0013 | `{"2": 19, "3": 13, "5": 4, "7": 10, "8": 1}` |
| `low_health` | 234 | -0.0025 | -0.0022 | `{"1": 62, "2": 1, "3": 72, "4": 5, "5": 67, "7": 26, "8": 1}` |
| `no_major_pressure` | 32 | -0.0013 | -0.0006 | `{"1": 4, "2": 10, "3": 5, "4": 1, "5": 3, "7": 1, "8": 8}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
