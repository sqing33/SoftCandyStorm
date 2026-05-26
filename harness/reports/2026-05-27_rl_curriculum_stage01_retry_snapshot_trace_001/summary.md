# RL Curriculum Stage 01 Retry Snapshot Trace

- Source model: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Decision: `rl_snapshot_trace_recorded_needs_opening_repair`
- Evaluation: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_snapshot_trace_001/evaluation.json`
- Trace directory: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_snapshot_trace_001/traces`

## Trace Run

The run used `train_sb3.py --trace-dir --trace-failed-only --trace-sample-stride 30` after adding Gym snapshot diagnostics to trace rows. It replayed `soda-creek` seeds `62406` through `62409` for 60 seconds and wrote traces for the two failed policy episodes.

| Seed | Result | Time | Damage | Trace |
|---:|---|---:|---:|---|
| 62406 | `defeat` | 46.1996s | 120.26 | `traces/soda-creek_seed62406_trace.json` |
| 62409 | `defeat` | 28.8332s | 120.12 | `traces/soda-creek_seed62409_trace.json` |

## Findings

- Both failed episodes end at the `soda-creek` bottom-right corner: player position reaches `x = 1200.0`, `y = -900.0`, `boundary.min_distance = 0.0`, and `boundary.edge_risk = 1.0`.
- Both failures also have direct enemy contact at death: `nearest_enemy.hitbox_distance = 0.0`, `enemy_pressure_risk = 1.0`, and `nearby_enemy_count_160 = 7`.
- The policy keeps choosing action `4` with high confidence while already pinned to the edge. Final chosen action scores are `0.8741` for seed `62406` and `0.8494` for seed `62409`.
- The practical failure shape is now clear: stage 01 retry learned a bottom-right opening route that can pin the player into the map boundary before it escapes enemy pressure.

## Next

- Do not advance stage 02 as if the opening blocker is fixed.
- Compare successful seeds `62407` / `62408` against failed seeds with a non-failed-only trace run, focusing on when action `4` should switch away from the corner.
- Consider an opening repair that explicitly discourages continuing into zero boundary distance under enemy pressure, then re-run the 60-second high-pressure 10-seed comparison.
