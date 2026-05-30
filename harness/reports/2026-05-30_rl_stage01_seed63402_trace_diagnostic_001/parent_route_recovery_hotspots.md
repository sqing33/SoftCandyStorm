# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 3
- Sampled rows: 477
- Negative route_recovery rows: 277 (58.07%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `soda-creek` | 63401 | 6.6667 | `opening_lt_60` | 2 | -0.0022 | `boundary_edge` | 51.4736 | bouncy-gummy d=27.0945 | 2:0.3679, 3:0.2175, 4:0.1532 |
| `soda-creek` | 63400 | 55.9995 | `opening_lt_60` | 3 | -0.0021 | `boundary_edge` | 0.0 | soda-bubble d=0.0 | 3:0.6341, 4:0.2112, 5:0.0781 |
| `soda-creek` | 63400 | 8.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=884.6502 | 2:0.3401, 1:0.2454, 7:0.1014 |
| `soda-creek` | 63401 | 8.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=345.9562 | 2:0.2489, 4:0.175, 3:0.1641 |
| `soda-creek` | 63400 | 9.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=890.9779 | 2:0.3202, 1:0.2539, 7:0.1095 |
| `soda-creek` | 63401 | 9.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=356.9262 | 2:0.3468, 3:0.1677, 4:0.1474 |
| `soda-creek` | 63400 | 9.3333 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=898.2872 | 2:0.301, 1:0.262, 7:0.1178 |
| `soda-creek` | 63401 | 9.3333 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=369.4199 | 2:0.34, 3:0.1686, 4:0.1465 |
| `soda-creek` | 63400 | 9.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=883.835 | 2:0.2902, 1:0.266, 7:0.1223 |
| `soda-creek` | 63401 | 9.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=342.9959 | 2:0.4741, 1:0.1655, 3:0.1223 |
| `soda-creek` | 63400 | 10.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=499.4955 | 2:0.2843, 1:0.2677, 7:0.1244 |
| `soda-creek` | 63401 | 10.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=322.9959 | 2:0.4669, 1:0.17, 3:0.1201 |
| `soda-creek` | 63401 | 10.3334 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=346.3635 | 2:0.4517, 1:0.1484, 3:0.1389 |
| `soda-creek` | 63401 | 10.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=383.446 | 2:0.4455, 1:0.153, 3:0.1358 |
| `soda-creek` | 63401 | 11.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=363.446 | 2:0.3429, 3:0.1996, 4:0.1646 |
| `soda-creek` | 63401 | 11.3334 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=317.2128 | 2:0.4792, 3:0.1798, 4:0.1149 |
| `soda-creek` | 63401 | 11.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=297.2128 | 2:0.4809, 3:0.1868, 4:0.1105 |
| `soda-creek` | 63401 | 12.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=277.2128 | 2:0.4614, 3:0.1975, 4:0.1189 |
| `soda-creek` | 63401 | 12.3334 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=257.2128 | 2:0.4568, 3:0.1959, 4:0.1197 |
| `soda-creek` | 63401 | 12.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=162.2588 | 2:0.5181, 3:0.1776, 1:0.1093 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `soda-creek` | 277 | -0.0022 | -0.0013 | `{"2": 70, "3": 17, "4": 10, "5": 51, "7": 129}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `mid_60_to_180` | 1 | -0.0015 | -0.0015 | `{"3": 1}` |
| `opening_lt_60` | 276 | -0.0022 | -0.0013 | `{"2": 70, "3": 16, "4": 10, "5": 51, "7": 129}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 265 | -0.0022 | -0.0014 | `{"2": 61, "3": 17, "4": 7, "5": 51, "7": 129}` |
| `enemy_pressure` | 14 | -0.0018 | -0.0007 | `{"2": 1, "5": 5, "7": 8}` |
| `low_health` | 2 | -0.0018 | -0.001 | `{"5": 2}` |
| `no_major_pressure` | 12 | -0.0009 | -0.0005 | `{"2": 9, "4": 3}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
