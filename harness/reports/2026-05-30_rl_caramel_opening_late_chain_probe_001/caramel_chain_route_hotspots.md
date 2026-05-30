# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 3
- Sampled rows: 699
- Negative route_recovery rows: 181 (25.89%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 63400 | 59.9994 | `opening_lt_60` | 3 | -0.0125 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=435.335 | 3:0.5977, 4:0.1372, 5:0.0728 |
| `caramel-workshop` | 63401 | 7.0 | `opening_lt_60` | 2 | -0.012 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=0.0 | 2:0.3094, 3:0.2, 4:0.1939 |
| `caramel-workshop` | 63401 | 9.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=393.4287 | 2:0.3661, 3:0.1821, 4:0.148 |
| `caramel-workshop` | 63401 | 10.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=426.8413 | 2:0.2207, 3:0.1612, 4:0.1482 |
| `caramel-workshop` | 63401 | 11.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=381.8413 | 2:0.3374, 3:0.1585, 4:0.1305 |
| `caramel-workshop` | 63401 | 12.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=286.2908 | 2:0.3181, 1:0.1483, 3:0.146 |
| `caramel-workshop` | 63401 | 13.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=146.874 | 2:0.3136, 3:0.1953, 4:0.174 |
| `caramel-workshop` | 63402 | 13.0001 | `opening_lt_60` | 3 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=166.5189 | 3:0.3283, 4:0.288, 5:0.1714 |
| `caramel-workshop` | 63401 | 14.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=0.0 | 2:0.4348, 3:0.2056, 4:0.1424 |
| `caramel-workshop` | 63401 | 15.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=0.0 | 2:0.3262, 3:0.197, 4:0.1796 |
| `caramel-workshop` | 63402 | 15.0001 | `opening_lt_60` | 3 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=165.4881 | 3:0.3243, 4:0.2799, 2:0.1621 |
| `caramel-workshop` | 63401 | 16.0001 | `opening_lt_60` | 2 | -0.01 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=0.0 | 2:0.4679, 3:0.1614, 4:0.1287 |
| `caramel-workshop` | 63402 | 16.0001 | `opening_lt_60` | 3 | -0.01 | `boundary_edge` | 0.0 | caramel-slime d=157.7903 | 3:0.3264, 4:0.3239, 5:0.1746 |
| `caramel-workshop` | 63401 | 21.0 | `opening_lt_60` | 2 | -0.01 | `boundary_edge` | 0.0 | bouncy-gummy d=164.1313 | 2:0.3861, 3:0.2042, 4:0.1711 |
| `caramel-workshop` | 63401 | 22.0 | `opening_lt_60` | 2 | -0.0098 | `boundary_edge` | 0.0 | bouncy-gummy d=104.1312 | 2:0.3668, 3:0.2031, 4:0.1787 |
| `caramel-workshop` | 63400 | 44.9997 | `opening_lt_60` | 7 | -0.0087 | `boundary_edge`, `enemy_pressure`, `hazard_pressure` | 0.0 | bouncy-gummy d=0.0 | 7:0.4658, 0:0.1972, 6:0.1548 |
| `caramel-workshop` | 63401 | 17.0001 | `opening_lt_60` | 2 | -0.0082 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=67.0493 | 2:0.4614, 3:0.1597, 4:0.1335 |
| `caramel-workshop` | 63400 | 7.0 | `opening_lt_60` | 2 | -0.0074 | `boundary_edge` | 0.0 | caramel-slime d=909.7937 | 2:0.4807, 1:0.1617, 3:0.1228 |
| `caramel-workshop` | 63402 | 10.0 | `opening_lt_60` | 4 | -0.0071 | `boundary_edge` | 0.0 | bouncy-gummy d=289.5633 | 4:0.3483, 3:0.3037, 5:0.2467 |
| `caramel-workshop` | 63402 | 11.0 | `opening_lt_60` | 4 | -0.0071 | `boundary_edge` | 0.0 | caramel-slime d=291.4292 | 4:0.3193, 3:0.2928, 5:0.2838 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 181 | -0.0125 | -0.0044 | `{"1": 10, "2": 22, "3": 17, "4": 11, "5": 28, "7": 72, "8": 21}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 23 | -0.0021 | -0.0007 | `{"1": 4, "3": 3, "4": 3, "5": 5, "7": 2, "8": 6}` |
| `mid_60_to_180` | 51 | -0.0022 | -0.0008 | `{"1": 6, "3": 8, "4": 1, "5": 11, "7": 15, "8": 10}` |
| `opening_lt_60` | 107 | -0.0125 | -0.0068 | `{"2": 22, "3": 6, "4": 7, "5": 12, "7": 55, "8": 5}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 127 | -0.0125 | -0.0057 | `{"1": 5, "2": 19, "3": 7, "4": 7, "5": 19, "7": 62, "8": 8}` |
| `enemy_pressure` | 3 | -0.0087 | -0.0057 | `{"7": 3}` |
| `hazard_pressure` | 13 | -0.012 | -0.0074 | `{"2": 4, "7": 9}` |
| `low_health` | 32 | -0.0125 | -0.0015 | `{"1": 4, "3": 9, "4": 2, "5": 5, "7": 8, "8": 4}` |
| `no_major_pressure` | 34 | -0.0039 | -0.001 | `{"1": 3, "2": 3, "3": 4, "4": 3, "5": 8, "7": 4, "8": 9}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
