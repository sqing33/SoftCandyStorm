# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 8
- Sampled rows: 1202
- Negative route_recovery rows: 861 (71.63%)

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
| `soda-creek` | 63100 | 55.9995 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=287.6773 | 4:0.7817, 5:0.1772, 3:0.025 |
| `soda-creek` | 63101 | 55.9995 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=198.8593 | 7:0.9524, 8:0.0175, 0:0.0123 |
| `soda-creek` | 63101 | 56.9995 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | soda-bubble d=202.564 | 7:0.9557, 8:0.0161, 6:0.0119 |
| `soda-creek` | 63100 | 57.9995 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=232.4038 | 4:0.7834, 5:0.1758, 3:0.0251 |
| `soda-creek` | 63101 | 57.9995 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=163.7981 | 7:0.9549, 8:0.0167, 6:0.012 |
| `soda-creek` | 63100 | 58.9994 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=290.4278 | 4:0.782, 5:0.1768, 3:0.0257 |
| `soda-creek` | 63101 | 58.9994 | `opening_lt_60` | 7 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=218.0111 | 7:0.9575, 8:0.0155, 6:0.0116 |
| `soda-creek` | 63100 | 59.9994 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=190.8961 | 4:0.7946, 5:0.1696, 3:0.022 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 359 | -0.0023 | -0.0018 | `{"1": 6, "2": 72, "3": 192, "5": 13, "6": 3, "7": 42, "8": 31}` |
| `cracked-star-jar` | 234 | -0.0021 | -0.0016 | `{"2": 38, "3": 88, "5": 5, "6": 2, "7": 48, "8": 53}` |
| `soda-creek` | 268 | -0.0025 | -0.0018 | `{"2": 49, "3": 46, "4": 23, "5": 27, "7": 41, "8": 82}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 109 | -0.0025 | -0.0018 | `{"1": 4, "3": 48, "5": 18, "7": 5, "8": 34}` |
| `mid_60_to_180` | 446 | -0.0025 | -0.0018 | `{"1": 2, "3": 278, "5": 27, "6": 5, "7": 2, "8": 132}` |
| `opening_lt_60` | 306 | -0.0025 | -0.0016 | `{"2": 159, "4": 23, "7": 124}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boss_pressure` | 1 | -0.0016 | -0.0016 | `{"5": 1}` |
| `boundary_edge` | 830 | -0.0025 | -0.0018 | `{"1": 4, "2": 149, "3": 321, "4": 22, "5": 43, "6": 1, "7": 128, "8": 162}` |
| `enemy_pressure` | 23 | -0.002 | -0.001 | `{"2": 22, "7": 1}` |
| `hazard_pressure` | 37 | -0.0023 | -0.0014 | `{"1": 3, "2": 18, "5": 2, "7": 12, "8": 2}` |
| `low_health` | 117 | -0.0025 | -0.002 | `{"1": 2, "2": 1, "3": 46, "4": 4, "5": 4, "7": 27, "8": 33}` |
| `no_major_pressure` | 28 | -0.0013 | -0.0007 | `{"1": 2, "2": 10, "3": 4, "4": 1, "5": 2, "6": 4, "7": 3, "8": 2}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
