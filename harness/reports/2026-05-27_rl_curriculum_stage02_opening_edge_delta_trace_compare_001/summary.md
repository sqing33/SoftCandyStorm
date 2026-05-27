# RL Curriculum Stage 02 Opening Edge Delta Trace Compare

- Decision: `stage02_opening_edge_delta_trace_compare_recorded`
- Stage 02 model: `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_001/stage02_opening_edge_delta.zip`
- Stage 01 model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Seeds: `62400`, `62401`, `62403`, `62405`, `62409`

## Evaluation Summary

| Model | Win Rate | Avg Survival | Trace Scope |
|---|---:|---:|---|
| Stage 02 opening edge delta | 50.00% | 46.2796s | failed-only traces |
| Stage 01 corner risk delta | 100.00% | 60.0328s | same failed seed traces |

## Seed Comparison

| Seed | Stage 02 Result | Stage 02 Final Pressure | Stage 02 Action Pattern | Stage 01 Result | Stage 01 Final Pressure | Stage 01 Action Pattern |
|---:|---|---|---|---|---|---|
| 62400 | defeat at 24.0000s | edge 1.00, enemy 1.00, hitbox 6.772 | top 4 87.7%, first7 24, tail 44444447 | victory at 60.0328s | edge 1.00, enemy 0.00, hitbox 122.303 | top 7 57.1%, first7 25.9999, tail 77777777 |
| 62401 | defeat at 33.7332s | edge 1.00, enemy 1.00, hitbox 0 | top 4 93.2%, first7 none, tail 44444444 | victory at 60.0328s | edge 1.00, enemy 0.00, hitbox 183.5915 | top 7 46.2%, first7 32.6665, tail 77777777 |
| 62403 | defeat at 24.5000s | edge 1.00, enemy 1.00, hitbox 0 | top 4 86.7%, first7 24.5, tail 44444447 | victory at 60.0328s | edge 1.00, enemy 0.34, hitbox 53.2506 | top 7 55.5%, first7 26.9999, tail 77777777 |
| 62405 | defeat at 51.5662s | edge 1.00, enemy 0.26, hitbox 0 | top 7 52.6%, first7 24.6666, tail 77777777 | victory at 60.0328s | edge 1.00, enemy 0.13, hitbox 52.6849 | top 7 46.7%, first7 29.6666, tail 44444444 |
| 62409 | defeat at 28.8332s | edge 1.00, enemy 1.00, hitbox 0 | top 4 94.3%, first7 none, tail 44444444 | victory at 60.0328s | edge 1.00, enemy 0.00, hitbox 234.7579 | top 7 61.0%, first7 23.6666, tail 77777777 |

## Findings

- Stage 02 opening_edge_delta still reaches hard edges at roughly the same early timing as stage 01, so early edge contact alone does not explain failure.
- Seeds 62401 and 62409 never switch to action 7 before death; seeds 62400 and 62403 switch only on the terminal sample, too late to reduce pressure.
- Seed 62405 switches to action 7 much earlier but still dies at the left/bottom edge with nearest_enemy.hitbox_distance = 0, so action 7 alone is insufficient once pressure has already attached.
- Stage 01 same-seed successful traces consistently reduce final enemy pressure and preserve health after a sustained action 7 evacuation segment.

## Conclusion

The regression is not just missing the existence of action `7`. Four failed seeds either never switch or switch only at the terminal sample, while seed `62405` switches to action `7` earlier but dies after pressure is already attached. The useful stage 01 behavior is a timely and sustained evacuation segment that reduces enemy pressure, not merely a lower edge-risk scalar.

## Next

- Prefer successful-trajectory replay or behavior constraints around the first edge + enemy-pressure window before changing scalar reward weights again.
- If another reward is attempted, target pressure reduction while edge risk is high and verify it with the same 60-second 10 seed gate before any 180-second comparison.
