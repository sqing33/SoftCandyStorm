# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 1
- Sampled rows: 82
- Negative route_recovery rows: 51 (62.20%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 63402 | 9.0 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 2.7313 | caramel-slime d=215.1644 | 4:0.465, 3:0.2593, 5:0.2237 |
| `caramel-workshop` | 63402 | 9.5 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=321.4855 | 4:0.3728, 3:0.3018, 5:0.2386 |
| `caramel-workshop` | 63402 | 10.0 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=289.5633 | 4:0.3502, 3:0.2984, 5:0.2508 |
| `caramel-workshop` | 63402 | 10.5 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=270.7803 | 4:0.3488, 5:0.2779, 3:0.2759 |
| `caramel-workshop` | 63402 | 11.0 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=291.4292 | 4:0.3205, 3:0.2888, 5:0.2881 |
| `caramel-workshop` | 63402 | 11.5 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=295.939 | 4:0.339, 5:0.2832, 3:0.2778 |
| `caramel-workshop` | 63402 | 12.0 | `opening_lt_60` | 4 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=310.0903 | 4:0.3191, 5:0.2865, 3:0.2796 |
| `caramel-workshop` | 63402 | 17.5001 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=417.2691 | 5:0.6771, 6:0.1293, 4:0.096 |
| `caramel-workshop` | 63402 | 18.0001 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=387.2693 | 5:0.7135, 6:0.1351, 4:0.0863 |
| `caramel-workshop` | 63402 | 18.5001 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=400.7499 | 5:0.7284, 6:0.1449, 4:0.0739 |
| `caramel-workshop` | 63402 | 19.0001 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=83.9788 | 5:0.7397, 6:0.1451, 4:0.0777 |
| `caramel-workshop` | 63402 | 19.5 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=61.4788 | 5:0.7356, 6:0.1494, 4:0.0763 |
| `caramel-workshop` | 63402 | 20.0 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=38.9788 | 5:0.7306, 6:0.1523, 4:0.0769 |
| `caramel-workshop` | 63402 | 20.5 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=280.7505 | 5:0.7383, 6:0.142, 4:0.077 |
| `caramel-workshop` | 63402 | 21.0 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=250.7508 | 5:0.7338, 6:0.1449, 4:0.0764 |
| `caramel-workshop` | 63402 | 22.0 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=190.7513 | 5:0.724, 6:0.1493, 4:0.0774 |
| `caramel-workshop` | 63402 | 22.5 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | bouncy-gummy d=160.7515 | 5:0.7169, 6:0.1549, 4:0.0751 |
| `caramel-workshop` | 63402 | 23.0 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=237.5166 | 5:0.743, 6:0.1313, 4:0.0905 |
| `caramel-workshop` | 63402 | 23.5 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=215.0166 | 5:0.739, 6:0.1343, 4:0.0899 |
| `caramel-workshop` | 63402 | 24.0 | `opening_lt_60` | 5 | -0.0014 | `boundary_edge` | 0.0 | caramel-slime d=192.5166 | 5:0.7397, 6:0.1285, 4:0.1042 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 51 | -0.0014 | -0.0012 | `{"2": 2, "4": 10, "5": 39}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `opening_lt_60` | 51 | -0.0014 | -0.0012 | `{"2": 2, "4": 10, "5": 39}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boundary_edge` | 47 | -0.0014 | -0.0012 | `{"4": 8, "5": 39}` |
| `enemy_pressure` | 6 | -0.0014 | -0.0006 | `{"5": 6}` |
| `hazard_pressure` | 6 | -0.0014 | -0.0006 | `{"5": 6}` |
| `no_major_pressure` | 4 | -0.0008 | -0.0005 | `{"2": 2, "4": 2}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
