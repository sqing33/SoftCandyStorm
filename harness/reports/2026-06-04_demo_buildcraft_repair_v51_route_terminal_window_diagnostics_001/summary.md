# RouteBot Trajectory Window Diagnostic

- Decision: `route_bot_trajectory_window_valid`
- Recommendation: `use_seed_specific_window_diagnostics_for_v54_repair`
- Candidate: `2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Content hash: `fnv1a64:50bd536bd0669e2b`
- Bot / map: `route` / `frosting-grassland`
- Samples: `240`
- Upgrade samples: `1`
- Victories / defeats: `4` / `6`
- Sampled victories / defeats: `4` / `0`
- Missing-window seeds: `[72001, 72002, 72003, 72005, 72007, 72008]`

## Group Summary

| Group | Seeds | Sampled Seeds | Health | Edge Risk | Enemy Risk | Boss Risk | Safety Risk | Nearby 160 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `victory` | `[72000, 72004, 72006, 72009]` | `[72000, 72004, 72006, 72009]` | 0.2043 | 0.0000 | 0.0009 | 0.0000 | 0.1002 | 0.2042 |
| `defeat` | `[72001, 72002, 72003, 72005, 72007, 72008]` | `[]` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Seeds

| Seed | Terminal | Level | Damage | Health | Edge Risk | Enemy Risk | Safety Risk | Top Nearest Enemies |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 72000 | `victory` | 6 | 82.780 | 0.3102 | 0.0000 | 0.0008 | 0.0275 | sandwich-cookie-creep:17, bouncy-gummy:11, licorice-skipper:10, sticky-bear-gummy:6, sour-gummy:5 |
| 72001 | `defeat` | 5 | 120.390 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72002 | `defeat` | 6 | 120.671 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72003 | `defeat` | 5 | 120.397 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72004 | `victory` | 7 | 108.677 | 0.0944 | 0.0000 | 0.0018 | 0.1758 | bouncy-gummy:16, licorice-skipper:14, sandwich-cookie-creep:10, sprinkle-spitter:7, sour-gummy:5 |
| 72005 | `defeat` | 3 | 136.124 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72006 | `victory` | 7 | 103.747 | 0.1354 | 0.0000 | 0.0011 | 0.1474 | bouncy-gummy:15, licorice-skipper:11, sugar-moth:8, sandwich-cookie-creep:7, sticky-bear-gummy:7 |
| 72007 | `defeat` | 6 | 136.270 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72008 | `defeat` | 7 | 121.533 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72009 | `victory` | 7 | 86.730 | 0.2772 | 0.0000 | 0.0000 | 0.0499 | licorice-skipper:15, bouncy-gummy:12, sandwich-cookie-creep:11, sugar-moth:7, sprinkle-spitter:6 |

## Upgrade Samples

- Seed `72004` at `250.42453`s chose `star-spoon` from `['pudding-turret', 'star-spoon', 'sour-plum-spray']`

## Limitations

- This report uses sampled Harness trajectory diagnostics, not full frame-by-frame replay state.
- It does not promote generated content or prove a gameplay fix.
- Human playtest evidence is still required before content acceptance.
