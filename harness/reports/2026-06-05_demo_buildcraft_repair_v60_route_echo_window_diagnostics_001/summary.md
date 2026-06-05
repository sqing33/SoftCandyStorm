# v60 Route Echo Window Diagnostics

- Candidate: `harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v60_full_pack`
- Bot / map: `route` / `frosting-grassland`
- Seeds: `72000`..`72009`
- Window: `210`..`234` seconds
- Samples: `304`
- Upgrade samples exported: `9`
- Content hash: `fnv1a64:cd1295a2515e4a57`

## Decision

- Decision: `route_echo_window_underpowered`
- Recommendation: `widen_deterministic_route_echo_for_v61`

## Key Findings

The v60 event does not reliably affect the RouteBot winning seeds. In the 216-232 second window:

| Seed | Route Result | Avg Active Hazards | Avg Hazard Risk | Min Health | Notes |
|---:|---|---:|---:|---:|---|
| 72000 | victory | 0.00 | 0.000 | 0.310 | No effective route echo pressure during the upgrade/Boss entry window. |
| 72004 | victory | 0.75 | 0.127 | 0.094 | Some hazards appear, but pressure is too low to convert the run. |
| 72006 | victory | 0.28 | 0.162 | 0.135 | Hazards are intermittent and do not disrupt survival. |
| 72009 | victory | 0.22 | 0.114 | 0.277 | Hazards are mostly absent around upgrade choices. |

Defeat seeds often show higher hazard pressure, which means v60 is not targeting the specific residual winning routes:

| Seed | Route Result | Avg Active Hazards | Avg Hazard Risk | Min Health |
|---:|---|---:|---:|---:|
| 72001 | defeat | 0.40 | 0.383 | 0.019 |
| 72002 | defeat | 0.88 | 0.404 | 0.022 |
| 72003 | defeat | 0.38 | 0.362 | 0.036 |
| 72007 | defeat | 0.33 | 0.316 | 0.037 |
| 72008 | defeat | 1.06 | 0.336 | 0.161 |

## Upgrade Window Notes

- Seed `72000` chose `nonstick-apron` at `216.72`s with `active_hazard_count` 0.
- Seed `72009` chose `pudding-turret` at `221.89`s and `bubble-shoes` at `228.29`s with `active_hazard_count` 0.
- Seed `72004` and `72006` had some hazards near upgrades, but still converted to victories.

## Conclusion

v60 proves that a deterministic `chance=1.0` event can preserve the healthy `kite`, `random`, `greedy`, and `zone-control` baselines, but its route echo parameters are too narrow for the actual residual RouteBot winning paths.

v61 should keep deterministic triggering, but use a wider and earlier route echo window, closer to the v55 effective route-counter shape without reintroducing probabilistic RNG side effects.

## Limitations

- This diagnostic uses sampled trajectory data, not every fixed tick.
- The exported replay format does not directly label content event IDs or individual route echo hazard sources.
- This report does not promote v60; v60 remains rejected for RouteBot underrepair.
