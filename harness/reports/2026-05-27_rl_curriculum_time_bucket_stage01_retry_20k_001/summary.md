# RL Curriculum Stage 01 Retry 20k

- Previous stage: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_opening_001/summary.md`
- Decision: `rl_curriculum_stage01_retry_recorded_needs_opening_repair`
- Model: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Failure case: `harness/failed_cases/fail_20260527_019_curriculum_stage01_retry_soda_opening_gap.json`

## Training

- Warm start: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`
- Maps: `cracked-star-jar`, `soda-creek`
- Map selection: `random`
- Train seconds: 60
- Requested timesteps: 20000
- Actual timesteps: 20224
- Entropy coefficient: 0.02
- Report: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/ppo_training_report.json`

## 60s High-pressure 10-seed Comparison

| Map | Win Rate | Avg Survival | Dominant Action | Entropy | Best Rule Bot |
|---|---:|---:|---|---:|---:|
| `soda-creek` | 80.00% | 55.5295s | `7` / 41.23% | 0.5027 | 100.00% |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 43.40% | 0.5096 | 100.00% |
| `cracked-star-jar` | 100.00% | 60.0328s | `7` / 46.41% | 0.5134 | 100.00% |

The retry improved `soda-creek` from 66.67% to 80.00%, but it still failed two opening seeds:

| Seed | Time | Reason | Level | Kills | Damage | Dominant Action |
|---:|---:|---|---:|---:|---:|---|
| 62406 | 46.1996s | `player_health_depleted` | 1 | 38 | 120.26 | `4` / 69.99% |
| 62409 | 28.8332s | `player_health_depleted` | 1 | 25 | 120.1198 | `4` / 94.91% |

## Next

- Keep the curriculum blocked at stage 01; do not treat opening survival as fixed.
- The next repair should inspect `soda-creek` opening trajectories and action `4` failure paths instead of only adding more generic PPO timesteps.
- Stage 02 mid-run training should wait until the opening bucket is stable or explicitly branch from a known-repair checkpoint.
