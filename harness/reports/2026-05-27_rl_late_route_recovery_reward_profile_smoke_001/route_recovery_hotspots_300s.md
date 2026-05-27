# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 9
- Sampled rows: 1100
- Negative route_recovery rows: 841 (76.45%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 62301 | 180.0095 | `late_180_to_300` | 4 | -0.015 | `boundary_edge`, `hazard_pressure` | 0.0 | sour-gummy d=318.8943 | 4:0.4418, 3:0.2726, 2:0.1385 |
| `caramel-workshop` | 62301 | 181.0097 | `late_180_to_300` | 4 | -0.015 | `boundary_edge`, `hazard_pressure` | 0.0 | sticky-bear-gummy d=445.1991 | 4:0.5631, 3:0.202, 2:0.1044 |
| `caramel-workshop` | 62301 | 182.0099 | `late_180_to_300` | 4 | -0.015 | `boundary_edge`, `hazard_pressure` | 0.0 | sticky-bear-gummy d=393.199 | 4:0.5593, 3:0.2044, 2:0.1071 |
| `soda-creek` | 62301 | 183.0101 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=520.4708 | 4:0.3947, 3:0.2825, 2:0.1685 |
| `soda-creek` | 62301 | 184.0103 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=463.6547 | 4:0.3816, 3:0.287, 2:0.1761 |
| `caramel-workshop` | 62301 | 187.011 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | caramel-slime d=461.2462 | 4:0.3704, 3:0.2874, 2:0.2021 |
| `caramel-workshop` | 62301 | 200.0138 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | caramel-slime d=492.8106 | 4:0.3818, 3:0.2888, 2:0.1913 |
| `caramel-workshop` | 62301 | 201.014 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | caramel-slime d=447.8101 | 4:0.4037, 3:0.2756, 2:0.1911 |
| `soda-creek` | 62301 | 201.014 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=552.118 | 4:0.7201, 3:0.1158, 5:0.109 |
| `soda-creek` | 62301 | 202.0142 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=508.8206 | 4:0.7026, 3:0.1269, 5:0.1092 |
| `caramel-workshop` | 62301 | 203.0144 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=500.8259 | 4:0.3671, 3:0.2997, 2:0.1831 |
| `soda-creek` | 62301 | 203.0144 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=448.8206 | 4:0.6935, 3:0.1328, 5:0.1089 |
| `soda-creek` | 62301 | 204.0146 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=459.2606 | 4:0.7374, 5:0.1099, 3:0.102 |
| `soda-creek` | 62301 | 205.0148 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=724.4292 | 4:0.3853, 3:0.2898, 2:0.1863 |
| `caramel-workshop` | 62300 | 206.0151 | `late_180_to_300` | 4 | -0.015 | `boundary_edge`, `low_health` | 0.0 | bouncy-gummy d=349.2794 | 4:0.7265, 5:0.1122, 3:0.1109 |
| `soda-creek` | 62301 | 206.0151 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=664.4292 | 4:0.3807, 3:0.2915, 2:0.1892 |
| `caramel-workshop` | 62300 | 207.0153 | `late_180_to_300` | 4 | -0.015 | `boundary_edge`, `hazard_pressure`, `low_health` | 0.0 | sour-gummy d=455.1058 | 4:0.5165, 3:0.2432, 2:0.1122 |
| `soda-creek` | 62301 | 207.0153 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=604.4292 | 4:0.6676, 3:0.1499, 5:0.108 |
| `caramel-workshop` | 62300 | 208.0155 | `late_180_to_300` | 4 | -0.015 | `boundary_edge`, `hazard_pressure`, `low_health` | 0.0 | sour-gummy d=417.9394 | 4:0.4452, 3:0.2849, 2:0.1191 |
| `soda-creek` | 62301 | 208.0155 | `late_180_to_300` | 4 | -0.015 | `boundary_edge` | 0.0 | bouncy-gummy d=544.4292 | 4:0.3673, 3:0.2953, 2:0.1994 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 441 | -0.015 | -0.0041 | `{"2": 39, "3": 60, "4": 253, "7": 89}` |
| `cracked-star-jar` | 150 | -0.0022 | -0.0014 | `{"2": 7, "4": 87, "7": 56}` |
| `soda-creek` | 250 | -0.015 | -0.004 | `{"2": 20, "3": 11, "4": 127, "7": 92}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 92 | -0.015 | -0.0115 | `{"2": 9, "3": 24, "4": 51, "7": 8}` |
| `mid_60_to_180` | 379 | -0.0147 | -0.0038 | `{"2": 33, "3": 45, "4": 210, "7": 91}` |
| `opening_lt_60` | 370 | -0.0025 | -0.0014 | `{"2": 24, "3": 2, "4": 206, "7": 138}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 818 | -0.015 | -0.0036 | `{"2": 61, "3": 71, "4": 449, "7": 237}` |
| `enemy_pressure` | 31 | -0.0023 | -0.001 | `{"4": 12, "7": 19}` |
| `hazard_pressure` | 96 | -0.015 | -0.0048 | `{"2": 9, "3": 7, "4": 54, "7": 26}` |
| `low_health` | 109 | -0.015 | -0.006 | `{"4": 67, "7": 42}` |
| `no_major_pressure` | 20 | -0.007 | -0.0011 | `{"2": 5, "4": 15}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
