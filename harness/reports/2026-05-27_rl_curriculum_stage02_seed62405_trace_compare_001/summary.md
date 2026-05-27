# RL Curriculum Stage 02 Seed 62405 Trace Compare

- Decision: `stage02_seed62405_trace_compare_recorded`
- Baseline model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Regression model: `harness/reports/2026-05-27_rl_curriculum_stage02_seed_replay_short_001/stage02_seed_replay_short.zip`
- Map: `soda-creek`
- Seed: `62405`

## Result

| Model | Terminal | Time | Sampled Action Mix | Key Route |
|---|---|---:|---|---|
| stage 01 `corner_risk_delta` | victory | 60.0328s | `7` 46.7%, `4` 44.5%, `2` 6.6%, `3` 2.2% | reaches bottom-right, then switches to `7` at 29.6666s and moves left along the bottom edge |
| stage 02 `seed_replay_short` | defeat | 47.3330s | `4` 56.6%, `2` 43.4% | runs `2` to the top-right, then `4` down the right edge into the bottom-right corner and never switches to `7` |

## Key Trace Points

- Stage 01 reaches right/bottom corner pressure by `28.3332s` with health `92.9898`, then switches from action `4` to action `7` at `29.6666s` while enemy pressure is still `1.0`; it survives the 60-second gate.
- Stage 02 reaches the top-right edge earlier, switches from action `2` to `4` at `20.6667s`, and stays on the right edge until death.
- Stage 02 hits low-health risk at `45.9996s` in the bottom-right corner with `enemy_pressure_risk = 1.0`, then keeps high-confidence action `4` until `player_health_depleted`.

## Conclusion

Seed replay improved coverage but did not preserve the stage 01 escape trigger. The remaining blocker is not just seed exposure; the policy needs a stronger constraint that rewards or supervises switching away from the right-side corner when enemy pressure rises.

## Next

- Add targeted opening regularization around right-edge / bottom-right pressure states.
- Re-run the 60-second high-pressure 10 seed gate before any 180-second stage 02 comparison.
