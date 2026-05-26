# RL Curriculum Stage 01 Retry Snapshot Compare

- Source model: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Decision: `rl_snapshot_compare_recorded_needs_opening_repair`
- Evaluation: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_snapshot_compare_001/evaluation.json`
- Trace directory: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_snapshot_compare_001/traces`

## Trace Run

This run repeated the `soda-creek` seeds `62406` through `62409` for 60 seconds with `--trace-dir` but without `--trace-failed-only`, so both failed and successful episodes have sampled snapshot diagnostics.

| Seed | Result | Time | Final Action | Final Health | Trace |
|---:|---|---:|---:|---:|---|
| 62406 | `defeat` | 46.1996s | `4` | 0.0 | `traces/soda-creek_seed62406_trace.json` |
| 62407 | `victory` | 60.0328s | `7` | 67.7296 | `traces/soda-creek_seed62407_trace.json` |
| 62408 | `victory` | 60.0328s | `7` | 73.7997 | `traces/soda-creek_seed62408_trace.json` |
| 62409 | `defeat` | 28.8332s | `4` | 0.0 | `traces/soda-creek_seed62409_trace.json` |

## Findings

- All four sampled episodes touch a map boundary early, so boundary contact alone is not the full failure signal.
- Failed seeds stay pinned at the right/bottom corner with a long tail of sampled action `4`: seed `62406` has 34 tail samples of action `4`; seed `62409` has 28.
- Successful seeds end with sampled action `7` and recover enemy pressure by the 60-second cutoff: final `enemy_pressure_risk = 0.0` for seeds `62407` and `62408`.
- The distinguishing signal is the lack of a timely reversal away from the right/bottom corner after enemy pressure rises. Seed `62409` never switches after reaching the corner; seed `62406` returns to a long action `4` tail and dies as nearby enemy count climbs.

## Next

- Repair should target the state-action pair: continuing action `4` while `boundary.min_distance = 0` near the right/bottom edge and `enemy_pressure_risk` is rising.
- Re-run the 60-second high-pressure 10-seed comparison after any reward or curriculum change; do not treat the successful seeds in this narrow window as policy acceptance.
