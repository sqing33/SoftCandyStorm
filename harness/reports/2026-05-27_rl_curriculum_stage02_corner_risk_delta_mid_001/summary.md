# RL Curriculum Stage 02 Corner Risk Delta Mid

- Previous stage: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/summary.md`
- Decision: `stage02_mid_corner_risk_delta_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage02_corner_risk_delta_mid_001/stage02_mid_corner_risk_delta.zip`
- Failure case: `harness/failed_cases/fail_20260527_022_stage02_corner_risk_delta_mid_regression.json`

## Change Under Test

- Warm-started from the stage 01 `corner_risk_delta` checkpoint.
- Trained a stage 02 mid-window PPO continuation on `caramel-workshop`.
- Training duration: `180s`
- Requested timesteps: `5000`
- Actual timesteps: `5120`
- Entropy coefficient: `0.02`

## Training Evaluation

Evaluation on `caramel-workshop`:

- Win rate: `100%`
- Average survival: `180.0095s`
- Dominant action: `2` / `55.99%`
- Normalized action entropy: `0.3160`
- Gate: `trained_needs_rule_bot_comparison`

## 180s High-pressure 3-seed Comparison

| Map | Win Rate | Avg Survival | Dominant Action | Entropy | Notes |
|---|---:|---:|---|---:|---|
| `soda-creek` | 33.33% | 136.6282s | `7` / 55.25% | 0.3134 | 2 defeats |
| `caramel-workshop` | 100.00% | 180.0095s | `2` / 77.81% | 0.2502 | action-bias repair |
| `cracked-star-jar` | 100.00% | 180.0095s | `7` / 51.05% | 0.4198 | no defeats |

Comparison gate: `multimap_comparison_recorded_needs_policy_repair`.

## Failure Analysis

- Total failures: `2`
- Repair maps: `soda-creek`
- `soda-creek` seed `62202` died at `52.7995s`, reopening the opening bucket.
- `soda-creek` seed `62201` died at `177.0755s`, inside the stage 02 mid-window.
- `caramel-workshop` survived all 3 seeds but triggered action-bias repair because action `2` reached `77.81%`.

## Conclusion

This stage 02 attempt is a regression, not a curriculum pass. Training only on `caramel-workshop` preserved that target map but moved the failure face back to `soda-creek`, including one opening death that stage 01 had just repaired.

Do not enter stage 03 from this checkpoint.

## Next

- Rework stage 02 to include stage 01 opening retention, such as mixed `soda-creek` opening seeds or a short replay/regularization check.
- Rerun both 60s opening regression and 180s mid-window comparison before treating stage 02 as passed.
