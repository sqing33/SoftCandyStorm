# Route Recovery Trace Hotspots

- Decision: `route_recovery_trace_hotspots_recorded`
- Traces: 15
- Sampled rows: 8205
- Negative route_recovery rows: 6942 (84.61%)

## Worst Hotspots

| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |
|---|---:|---:|---|---:|---:|---|---:|---|---|
| `caramel-workshop` | 62402 | 6.3333 | `opening_lt_60` | 3 | -0.0025 | `boundary_edge` | 9.9999 | bouncy-gummy d=0.0 | 3:0.7961, 4:0.0689, 2:0.0552 |
| `soda-creek` | 62400 | 23.0 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=32.023 | 4:0.3973, 5:0.3023, 3:0.1952 |
| `soda-creek` | 62401 | 34.7998 | `opening_lt_60` | 4 | -0.0025 | `boundary_edge`, `enemy_pressure`, `low_health` | 0.0 | soda-bubble d=0.0 | 4:0.5282, 5:0.2961, 3:0.0938 |
| `caramel-workshop` | 62401 | 116.6652 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | caramel-slime d=13.4674 | 2:0.5329, 3:0.3018, 1:0.1559 |
| `caramel-workshop` | 62401 | 119.9985 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge`, `hazard_pressure` | 0.0 | caramel-slime d=147.8323 | 2:0.6347, 1:0.249, 3:0.0957 |
| `caramel-workshop` | 62401 | 122.9985 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | sour-gummy d=255.1696 | 2:0.6405, 1:0.2519, 3:0.0926 |
| `caramel-workshop` | 62401 | 123.3318 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | sour-gummy d=281.5575 | 2:0.6214, 1:0.2957, 3:0.0695 |
| `caramel-workshop` | 62401 | 123.6651 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | sour-gummy d=268.7916 | 2:0.5876, 1:0.3311, 3:0.066 |
| `caramel-workshop` | 62401 | 123.9985 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | caramel-slime d=466.329 | 2:0.6209, 1:0.2863, 3:0.0804 |
| `caramel-workshop` | 62401 | 124.3318 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | caramel-slime d=451.3292 | 2:0.632, 1:0.2751, 3:0.0797 |
| `caramel-workshop` | 62401 | 124.6651 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=0.0 | 2:0.6222, 1:0.2519, 3:0.1124 |
| `caramel-workshop` | 62401 | 124.9984 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | sour-gummy d=173.1027 | 2:0.6448, 1:0.232, 3:0.1086 |
| `caramel-workshop` | 62401 | 125.3318 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=403.7045 | 2:0.6414, 1:0.2366, 3:0.1071 |
| `caramel-workshop` | 62401 | 125.6651 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=253.8539 | 2:0.6064, 1:0.3154, 3:0.064 |
| `caramel-workshop` | 62401 | 125.9984 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=363.7045 | 2:0.6023, 1:0.2992, 3:0.085 |
| `caramel-workshop` | 62401 | 126.3317 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=343.7045 | 2:0.6011, 1:0.3003, 3:0.0851 |
| `caramel-workshop` | 62401 | 126.6651 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=333.662 | 2:0.5646, 1:0.3271, 3:0.0929 |
| `caramel-workshop` | 62401 | 126.9984 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=313.662 | 2:0.5601, 1:0.3347, 3:0.0896 |
| `caramel-workshop` | 62401 | 127.3317 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | bouncy-gummy d=293.662 | 2:0.5586, 1:0.3368, 3:0.0889 |
| `caramel-workshop` | 62401 | 127.6651 | `mid_60_to_180` | 2 | -0.0025 | `boundary_edge` | 0.0 | caramel-slime d=333.2812 | 2:0.5713, 1:0.3136, 3:0.0995 |

## Map Summary

| Map | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `caramel-workshop` | 2797 | -0.0025 | -0.0018 | `{"1": 1247, "2": 260, "3": 414, "4": 32, "5": 95, "6": 56, "7": 589, "8": 104}` |
| `cracked-star-jar` | 2354 | -0.0024 | -0.0017 | `{"1": 1503, "2": 102, "3": 354, "4": 35, "5": 274, "6": 72, "7": 3, "8": 11}` |
| `soda-creek` | 1791 | -0.0025 | -0.0018 | `{"1": 1102, "2": 167, "3": 207, "4": 19, "5": 166, "6": 5, "7": 105, "8": 20}` |

## Time Bucket Summary

| Bucket | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `late_180_to_300` | 1180 | -0.0025 | -0.0019 | `{"1": 717, "2": 62, "3": 40, "6": 129, "7": 232}` |
| `mid_60_to_180` | 3911 | -0.0025 | -0.0018 | `{"1": 2795, "2": 464, "3": 104, "4": 9, "5": 14, "7": 464, "8": 61}` |
| `opening_lt_60` | 1851 | -0.0025 | -0.0015 | `{"1": 340, "2": 3, "3": 831, "4": 77, "5": 521, "6": 4, "7": 1, "8": 74}` |

## Pressure Summary

| Pressure | Hotspots | Min | Avg | Actions |
|---|---:|---:|---:|---|
| `boss_pressure` | 39 | -0.0024 | -0.0013 | `{"1": 25, "2": 2, "6": 8, "7": 4}` |
| `boundary_edge` | 6839 | -0.0025 | -0.0018 | `{"1": 3834, "2": 525, "3": 913, "4": 85, "5": 535, "6": 122, "7": 690, "8": 135}` |
| `enemy_pressure` | 101 | -0.0025 | -0.001 | `{"1": 18, "2": 7, "3": 9, "4": 6, "5": 49, "6": 2, "7": 7, "8": 3}` |
| `hazard_pressure` | 281 | -0.0025 | -0.0015 | `{"1": 77, "2": 60, "3": 83, "4": 10, "5": 5, "6": 20, "7": 21, "8": 5}` |
| `low_health` | 431 | -0.0025 | -0.0023 | `{"1": 357, "2": 11, "3": 2, "4": 1, "5": 7, "6": 25, "7": 4, "8": 24}` |
| `no_major_pressure` | 102 | -0.0018 | -0.0007 | `{"1": 18, "2": 4, "3": 61, "4": 1, "6": 11, "7": 7}` |

## Limitations

- This report analyzes sampled trace rows only; unsampled frames are not inspected.
- Trace diagnostics are not full GameCore snapshots and do not replace Replay.
- A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.
