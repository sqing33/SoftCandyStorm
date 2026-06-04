# RouteBot Trajectory Window Diagnostic

- Decision: `route_bot_trajectory_window_valid`
- Recommendation: `use_seed_specific_window_diagnostics_for_v54_repair`
- Candidate: `2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Content hash: `fnv1a64:50bd536bd0669e2b`
- Bot / map: `route` / `frosting-grassland`
- Samples: `1338`
- Upgrade samples: `11`
- Victories / defeats: `4` / `6`
- Sampled victories / defeats: `4` / `5`
- Missing-window seeds: `[72005]`

## Group Summary

| Group | Seeds | Sampled Seeds | Health | Edge Risk | Enemy Risk | Boss Risk | Safety Risk | Nearby 160 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `victory` | `[72000, 72004, 72006, 72009]` | `[72000, 72004, 72006, 72009]` | 0.5571 | 0.0000 | 0.0171 | 0.0254 | 0.0524 | 0.4375 |
| `defeat` | `[72001, 72002, 72003, 72005, 72007, 72008]` | `[72001, 72002, 72003, 72007, 72008]` | 0.5302 | 0.0000 | 0.0216 | 0.0400 | 0.0420 | 0.5488 |

## Seeds

| Seed | Terminal | Level | Damage | Health | Edge Risk | Enemy Risk | Safety Risk | Top Nearest Enemies |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 72000 | `victory` | 6 | 82.780 | 0.5302 | 0.0000 | 0.0053 | 0.0236 | bouncy-gummy:60, sour-gummy:30, sugar-moth:18, sticky-bear-gummy:17, licorice-skipper:16 |
| 72001 | `defeat` | 5 | 120.390 | 0.3424 | 0.0000 | 0.0139 | 0.0439 | bouncy-gummy:60, sour-gummy:15, runaway-sugar-mixer:14, sticky-bear-gummy:13, licorice-skipper:12 |
| 72002 | `defeat` | 6 | 120.671 | 0.7784 | 0.0000 | 0.0229 | 0.0371 | bouncy-gummy:60, licorice-skipper:19, runaway-sugar-mixer:18, sticky-bear-gummy:12, sour-gummy:10 |
| 72003 | `defeat` | 5 | 120.397 | 0.4346 | 0.0000 | 0.0086 | 0.0376 | bouncy-gummy:70, sour-gummy:23, runaway-sugar-mixer:12, licorice-skipper:4, soda-bubble:4 |
| 72004 | `victory` | 7 | 108.677 | 0.4676 | 0.0000 | 0.0204 | 0.0825 | bouncy-gummy:59, sour-gummy:27, sticky-bear-gummy:21, licorice-skipper:20, runaway-sugar-mixer:18 |
| 72005 | `defeat` | 3 | 136.124 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | run ended before sampled window or no matching sample was exported |
| 72006 | `victory` | 7 | 103.747 | 0.6320 | 0.0000 | 0.0292 | 0.0703 | bouncy-gummy:54, sour-gummy:34, licorice-skipper:27, sticky-bear-gummy:21, sandwich-cookie-creep:19 |
| 72007 | `defeat` | 6 | 136.270 | 0.3183 | 0.0000 | 0.0152 | 0.0474 | bouncy-gummy:61, sour-gummy:20, licorice-skipper:12, sticky-bear-gummy:7, sugar-moth:7 |
| 72008 | `defeat` | 7 | 121.533 | 0.7771 | 0.0000 | 0.0474 | 0.0441 | bouncy-gummy:61, sour-gummy:21, licorice-skipper:16, runaway-sugar-mixer:13, sticky-bear-gummy:11 |
| 72009 | `victory` | 7 | 86.730 | 0.5984 | 0.0000 | 0.0136 | 0.0332 | bouncy-gummy:64, sour-gummy:26, licorice-skipper:21, sticky-bear-gummy:17, sugar-moth:15 |

## Upgrade Samples

- Seed `72000` at `216.71733`s chose `nonstick-apron` from `['soda-fountain', 'nonstick-apron', 'cream-clockwork']`
- Seed `72002` at `223.25206`s chose `nonstick-apron` from `['pudding-turret', 'bubble-shoes', 'nonstick-apron']`
- Seed `72004` at `184.37709`s chose `rainbow-candy-shot-level-5` from `['rainbow-candy-shot-level-5', 'marshmallow-shield', 'frosting-gloves']`
- Seed `72004` at `219.9847`s chose `sour-tuner` from `['pudding-turret', 'sour-tuner', 'soda-fountain']`
- Seed `72006` at `224.48566`s chose `sour-tuner` from `['sour-plum-spray', 'sour-tuner', 'lollipop-boomerang']`
- Seed `72006` at `227.61966`s chose `nonstick-apron` from `['sour-plum-spray', 'nonstick-apron', 'candy-crystal-lance']`
- Seed `72008` at `194.74597`s chose `star-spoon` from `['rainbow-candy-shot-level-5', 'mint-cyclone', 'star-spoon']`
- Seed `72008` at `212.01633`s chose `star-spoon` from `['rainbow-candy-shot-level-5', 'candy-crystal-lance', 'star-spoon']`
- Seed `72008` at `218.78444`s chose `rainbow-candy-shot-level-5` from `['rainbow-candy-shot-level-5', 'soda-fountain', 'nonstick-apron']`
- Seed `72009` at `221.8851`s chose `pudding-turret` from `['soda-fountain', 'frosting-gloves', 'pudding-turret']`
- Seed `72009` at `228.28647`s chose `bubble-shoes` from `['pudding-turret-level-2', 'soda-bubble-pop', 'bubble-shoes']`

## Limitations

- This report uses sampled Harness trajectory diagnostics, not full frame-by-frame replay state.
- It does not promote generated content or prove a gameplay fix.
- Human playtest evidence is still required before content acceptance.
