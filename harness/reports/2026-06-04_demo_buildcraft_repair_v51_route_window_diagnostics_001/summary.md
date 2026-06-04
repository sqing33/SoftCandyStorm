# RouteBot Trajectory Window Diagnostic

- Decision: `route_bot_trajectory_window_valid`
- Recommendation: `use_seed_specific_window_diagnostics_for_v54_repair`
- Candidate: `2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Content hash: `fnv1a64:50bd536bd0669e2b`
- Bot / map: `route` / `frosting-grassland`
- Samples: `267`
- Upgrade samples: `9`
- Victories / defeats: `4` / `6`
- Sampled victories / defeats: `4` / `5`
- Missing-window seeds: `[72005]`

## Group Summary

| Group | Seeds | Sampled Seeds | Health | Edge Risk | Enemy Risk | Boss Risk | Safety Risk | Nearby 160 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `victory` | `[72000, 72004, 72006, 72009]` | `[72000, 72004, 72006, 72009]` | 0.4410 | 0.0000 | 0.0250 | 0.0382 | 0.0801 | 0.6250 |
| `defeat` | `[72001, 72002, 72003, 72005, 72007, 72008]` | `[72001, 72002, 72003, 72007, 72008]` | 0.4666 | 0.0000 | 0.0419 | 0.0778 | 0.0838 | 0.8907 |

## Seeds

| Seed | Terminal | Level | Damage | Health | Edge Risk | Enemy Risk | Safety Risk | Top Nearest Enemies |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 72000 | `victory` | 6 | 82.780 | 0.4381 | 0.0000 | 0.0079 | 0.0369 | bouncy-gummy:7, licorice-skipper:6, sour-gummy:6, sugar-moth:6, sandwich-cookie-creep:5 |
| 72001 | `defeat` | 5 | 120.390 | 0.2927 | 0.0000 | 0.0281 | 0.0988 | bouncy-gummy:7, runaway-sugar-mixer:5, licorice-skipper:4, sticky-bear-gummy:2, sour-gummy:1 |
| 72002 | `defeat` | 6 | 120.671 | 0.6784 | 0.0000 | 0.0544 | 0.0769 | bouncy-gummy:7, runaway-sugar-mixer:6, licorice-skipper:4, sour-gummy:3, sugar-moth:3 |
| 72003 | `defeat` | 5 | 120.397 | 0.3867 | 0.0000 | 0.0140 | 0.0666 | bouncy-gummy:7, runaway-sugar-mixer:5, sour-gummy:4, soda-bubble:2, licorice-skipper:1 |
| 72004 | `victory` | 7 | 108.677 | 0.3424 | 0.0000 | 0.0299 | 0.1240 | bouncy-gummy:12, runaway-sugar-mixer:6, sandwich-cookie-creep:6, licorice-skipper:5, sour-gummy:4 |
| 72005 | `defeat` | 3 | 136.124 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72006 | `victory` | 7 | 103.747 | 0.4901 | 0.0000 | 0.0408 | 0.1092 | sour-gummy:13, bouncy-gummy:7, licorice-skipper:5, sandwich-cookie-creep:5, runaway-sugar-mixer:4 |
| 72007 | `defeat` | 6 | 136.270 | 0.2792 | 0.0000 | 0.0296 | 0.0956 | bouncy-gummy:7, licorice-skipper:3, sour-gummy:3, sticky-bear-gummy:2, sugar-moth:2 |
| 72008 | `defeat` | 7 | 121.533 | 0.6959 | 0.0000 | 0.0833 | 0.0813 | bouncy-gummy:8, sour-gummy:5, runaway-sugar-mixer:4, licorice-skipper:3, sugar-moth:3 |
| 72009 | `victory` | 7 | 86.730 | 0.4935 | 0.0000 | 0.0213 | 0.0504 | bouncy-gummy:12, runaway-sugar-mixer:5, sandwich-cookie-creep:5, sour-gummy:4, sugar-moth:4 |

## Upgrade Samples

- Seed `72000` at `216.71733`s chose `nonstick-apron` from `['soda-fountain', 'nonstick-apron', 'cream-clockwork']`
- Seed `72002` at `223.25206`s chose `nonstick-apron` from `['pudding-turret', 'bubble-shoes', 'nonstick-apron']`
- Seed `72004` at `219.9847`s chose `sour-tuner` from `['pudding-turret', 'sour-tuner', 'soda-fountain']`
- Seed `72006` at `224.48566`s chose `sour-tuner` from `['sour-plum-spray', 'sour-tuner', 'lollipop-boomerang']`
- Seed `72006` at `227.61966`s chose `nonstick-apron` from `['sour-plum-spray', 'nonstick-apron', 'candy-crystal-lance']`
- Seed `72008` at `212.01633`s chose `star-spoon` from `['rainbow-candy-shot-level-5', 'candy-crystal-lance', 'star-spoon']`
- Seed `72008` at `218.78444`s chose `rainbow-candy-shot-level-5` from `['rainbow-candy-shot-level-5', 'soda-fountain', 'nonstick-apron']`
- Seed `72009` at `221.8851`s chose `pudding-turret` from `['soda-fountain', 'frosting-gloves', 'pudding-turret']`
- Seed `72009` at `228.28647`s chose `bubble-shoes` from `['pudding-turret-level-2', 'soda-bubble-pop', 'bubble-shoes']`

## Limitations

- This report uses sampled Harness trajectory diagnostics, not full frame-by-frame replay state.
- It does not promote generated content or prove a gameplay fix.
- Human playtest evidence is still required before content acceptance.
