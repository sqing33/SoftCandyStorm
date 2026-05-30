# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 3
- Sampled rows: 477
- Negative route_recovery rows: 276 (57.86%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `soda-creek` | 63401 | 6.6667 | `opening_lt_60` | 2 | -0.0022 | `boundary_edge` | 51.4736 | bouncy-gummy d=27.0945 | 2:0.3667, 3:0.219, 4:0.1522 |
| `soda-creek` | 63400 | 55.9995 | `opening_lt_60` | 3 | -0.0021 | `boundary_edge` | 0.0 | soda-bubble d=0.0 | 3:0.6378, 4:0.2085, 5:0.077 |
| `soda-creek` | 63400 | 8.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=884.6502 | 2:0.3398, 1:0.2509, 7:0.0998 |
| `soda-creek` | 63401 | 8.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=345.9562 | 2:0.2499, 4:0.1729, 3:0.1644 |
| `soda-creek` | 63400 | 9.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=890.9779 | 2:0.3201, 1:0.2594, 7:0.1077 |
| `soda-creek` | 63401 | 9.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=356.9262 | 2:0.3475, 3:0.1676, 4:0.1454 |
| `soda-creek` | 63400 | 9.3333 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=898.2872 | 2:0.301, 1:0.2676, 7:0.1159 |
| `soda-creek` | 63401 | 9.3333 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=369.4199 | 2:0.3407, 3:0.1685, 4:0.1446 |
| `soda-creek` | 63400 | 9.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | soda-bubble d=883.835 | 2:0.2902, 1:0.2716, 7:0.1203 |
| `soda-creek` | 63401 | 9.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=342.9959 | 2:0.4729, 1:0.169, 3:0.1223 |
| `soda-creek` | 63400 | 10.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=499.4955 | 2:0.2844, 1:0.2733, 7:0.1224 |
| `soda-creek` | 63401 | 10.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=322.9959 | 2:0.4659, 1:0.1735, 3:0.1201 |
| `soda-creek` | 63401 | 10.3334 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=346.3635 | 2:0.4515, 1:0.1512, 3:0.1391 |
| `soda-creek` | 63401 | 10.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=383.446 | 2:0.4455, 1:0.1559, 3:0.1359 |
| `soda-creek` | 63401 | 11.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=363.446 | 2:0.3441, 3:0.2002, 4:0.1628 |
| `soda-creek` | 63401 | 11.3334 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=317.2128 | 2:0.4787, 3:0.1804, 4:0.1137 |
| `soda-creek` | 63401 | 11.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=297.2128 | 2:0.4799, 3:0.1876, 4:0.1095 |
| `soda-creek` | 63401 | 12.0 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=277.2128 | 2:0.4607, 3:0.1984, 4:0.1178 |
| `soda-creek` | 63401 | 12.3334 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=257.2128 | 2:0.4562, 3:0.1967, 4:0.1186 |
| `soda-creek` | 63401 | 12.6667 | `opening_lt_60` | 2 | -0.002 | `boundary_edge` | 0.0 | bouncy-gummy d=162.2588 | 2:0.5166, 3:0.1784, 1:0.1115 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `soda-creek` | 276 | -0.0022 | -0.0013 | `{"2": 70, "3": 17, "4": 10, "5": 50, "7": 129}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `mid_60_to_180` | 1 | -0.0015 | -0.0015 | `{"3": 1}` |
| `opening_lt_60` | 275 | -0.0022 | -0.0013 | `{"2": 70, "3": 16, "4": 10, "5": 50, "7": 129}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 264 | -0.0022 | -0.0014 | `{"2": 61, "3": 17, "4": 7, "5": 50, "7": 129}` |
| `enemy_pressure` | 13 | -0.0018 | -0.0007 | `{"2": 1, "5": 4, "7": 8}` |
| `low_health` | 2 | -0.0018 | -0.001 | `{"5": 2}` |
| `no_major_pressure` | 12 | -0.0009 | -0.0006 | `{"2": 9, "4": 3}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
