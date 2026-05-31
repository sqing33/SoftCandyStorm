# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 2
- Sampled rows: 356
- Negative route_recovery rows: 248 (69.66%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 63405 | 115.9986 | `mid_60_to_180` | 1 | -0.0022 | `boundary_edge` | 0.0 | sticky-bear-gummy d=26.534 | 1:0.6088, 2:0.1757, 8:0.1344 |
| `caramel-workshop` | 63405 | 130.999 | `mid_60_to_180` | 8 | -0.0022 | `boundary_edge`, `hazard_pressure` | 0.0 | sticky-bear-gummy d=293.7588 | 8:0.4495, 7:0.3126, 1:0.1082 |
| `caramel-workshop` | 63405 | 9.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=328.8873 | 2:0.3069, 1:0.1548, 3:0.1411 |
| `caramel-workshop` | 63405 | 9.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=328.8873 | 2:0.2985, 1:0.1568, 3:0.142 |
| `caramel-workshop` | 63405 | 10.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=0.0 | 2:0.3092, 3:0.2074, 4:0.1744 |
| `caramel-workshop` | 63405 | 10.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=0.0 | 2:0.3009, 3:0.2106, 4:0.1715 |
| `caramel-workshop` | 63405 | 14.0001 | `opening_lt_60` | 3 | -0.002 | `boundary_edge`, `hazard_pressure` | 0.0 | bouncy-gummy d=407.1966 | 3:0.2673, 2:0.246, 4:0.2238 |
| `caramel-workshop` | 63405 | 15.0001 | `opening_lt_60` | 3 | -0.002 | `boundary_edge`, `hazard_pressure` | 0.0 | bouncy-gummy d=347.1964 | 3:0.2559, 2:0.2391, 4:0.2278 |
| `caramel-workshop` | 63405 | 25.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=426.7594 | 7:0.5245, 0:0.1869, 8:0.1352 |
| `caramel-workshop` | 63405 | 26.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=366.7592 | 7:0.5434, 0:0.191, 8:0.1265 |
| `caramel-workshop` | 63405 | 27.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=365.4299 | 7:0.5087, 0:0.2299, 8:0.1064 |
| `caramel-workshop` | 63405 | 28.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=305.4299 | 7:0.484, 0:0.2387, 6:0.1452 |
| `caramel-workshop` | 63405 | 29.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=364.199 | 7:0.5089, 0:0.1991, 6:0.1697 |
| `caramel-workshop` | 63405 | 30.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=364.7871 | 7:0.514, 0:0.1829, 6:0.1782 |
| `caramel-workshop` | 63405 | 31.9999 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | caramel-slime d=345.1907 | 7:0.5003, 6:0.2027, 0:0.1715 |
| `caramel-workshop` | 63405 | 32.9998 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | caramel-slime d=300.1908 | 7:0.4672, 0:0.2056, 6:0.1992 |
| `caramel-workshop` | 63405 | 32.9998 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=455.9999 | 7:0.434, 6:0.2604, 0:0.1266 |
| `caramel-workshop` | 63405 | 33.9998 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=249.3351 | 7:0.5001, 0:0.2163, 6:0.1332 |
| `caramel-workshop` | 63405 | 33.9998 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=395.9999 | 7:0.4342, 6:0.2435, 0:0.1395 |
| `caramel-workshop` | 63405 | 34.9998 | `opening_lt_60` | 7 | -0.002 | `boundary_edge` | 0.0 | caramel-slime d=219.1328 | 7:0.5556, 0:0.1539, 8:0.1157 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 248 | -0.0022 | -0.0017 | `{"1": 31, "2": 10, "3": 54, "4": 5, "5": 78, "7": 48, "8": 22}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 25 | -0.002 | -0.0017 | `{"5": 17, "8": 8}` |
| `mid_60_to_180` | 156 | -0.0022 | -0.0017 | `{"1": 31, "3": 50, "5": 59, "7": 2, "8": 14}` |
| `opening_lt_60` | 67 | -0.002 | -0.0016 | `{"2": 10, "3": 4, "4": 5, "5": 2, "7": 46}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boss_pressure` | 1 | -0.0016 | -0.0016 | `{"8": 1}` |
| `boundary_edge` | 236 | -0.0022 | -0.0017 | `{"1": 30, "2": 8, "3": 52, "4": 4, "5": 76, "7": 46, "8": 20}` |
| `enemy_pressure` | 8 | -0.0014 | -0.0008 | `{"1": 1, "3": 1, "5": 1, "7": 5}` |
| `hazard_pressure` | 33 | -0.0022 | -0.0014 | `{"1": 5, "3": 8, "5": 7, "7": 8, "8": 5}` |
| `low_health` | 2 | -0.0016 | -0.0013 | `{"3": 1, "8": 1}` |
| `no_major_pressure` | 12 | -0.0013 | -0.0007 | `{"1": 1, "2": 2, "3": 2, "4": 1, "5": 2, "7": 2, "8": 2}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
