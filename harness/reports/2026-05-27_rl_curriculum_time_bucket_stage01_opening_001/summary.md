# RL Curriculum Stage 01 Opening

- Source plan: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/summary.md`
- Decision: `rl_curriculum_stage01_recorded_needs_opening_repair`
- Model: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`
- Failure case: `harness/failed_cases/fail_20260527_018_curriculum_stage01_soda_opening_gap.json`

## Training

- Warm start: `harness/reports/2026-05-27_rl_ppo_time_phase_balance_closed_loop_10k_001/ppo_time_phase_balance_closed_loop_10k.zip`
- Maps: `cracked-star-jar`, `soda-creek`
- Map selection: `random`
- Train seconds: 60
- Requested timesteps: 5000
- Actual timesteps: 5120
- Entropy coefficient: 0.02
- Report: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/ppo_training_report.json`

## 60s High-pressure Comparison

| Map | Win Rate | Avg Survival | Dominant Action | Entropy | Best Rule Bot |
|---|---:|---:|---|---:|---:|
| `soda-creek` | 66.67% | 49.744s | `2` / 49.52% | 0.4718 | 100.00% |
| `caramel-workshop` | 100.00% | 60.0328s | `2` / 39.89% | 0.6047 | 100.00% |
| `cracked-star-jar` | 100.00% | 60.0328s | `3` / 34.33% | 0.5917 | 100.00% |

The comparison did not show the old deterministic action 3 collapse, but `soda-creek` still failed one seed: seed `62101` died at `29.1666s` with `player_health_depleted` after taking `119.9999` damage. This means stage 01 is useful repair evidence, not an accepted curriculum step.

## Next

- Do not treat stage 01 as an RL policy gate.
- Before chaining into stage 02 as if opening were fixed, either extend stage 01 training or rerun the opening stage with more seeds.
- Keep the failure bucket split: this result still points at `soda-creek` opening survival, not a generic 300-second average win-rate problem.
