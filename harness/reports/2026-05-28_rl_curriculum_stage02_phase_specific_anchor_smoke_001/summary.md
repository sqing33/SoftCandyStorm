# Stage 02 Phase-Specific Anchor Smoke

## 结论

- Gate decision: `policy_window_regression_failed`
- Model: `ppo_phase_specific_anchor_smoke.zip`
- Start model: `../2026-05-28_rl_curriculum_stage02_opening_aware_late_win_conversion_probe_001/ppo_distilled_opening_aware.zip`
- Anchor fallback: `../2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening: `../2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Training: `1024` PPO timesteps, `late-win-conversion`, `learning_rate=2e-05`, `ent_coef=0.02`
- Anchor regularization: full `36426` samples, `map_time_bucket_balance`, `weight=1.0`, `512` timestep interval, `2` KL epochs per interval, `opening=1.5x`, `mid=1.25x`, `late=0.75x`
- Failure case: `fail_20260528_084`

本报告验证 phase-specific anchor multipliers 是否比上一轮 full-dataset global `weight=2.0` 更稳。结果仍失败，不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

训练内 final validation 为 mean KL `0.342834`、argmax agreement `0.6798`。全量 anchor alignment 也失败：overall mean KL `0.345606`，overall argmax agreement `0.6841`。分桶看，opening mean KL 降到 `0.220892`，但 opening argmax agreement 仍只有 `0.5769`；mid `60-180s` mean KL 仍为 `0.440395`，argmax agreement `0.6301`。late `180-300s` argmax agreement 接近阈值，为 `0.7491`，但不足以解除整体漂移。

## Fixed Windows

| Window | Soda Creek | Caramel Workshop | Cracked Star Jar | Decision |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `0.6667` | `0.6667` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

Compared with the immediately previous opening-aware PPO probe, this run has `1` no-regression blocker: `caramel-workshop` 300s average survival drops by `5.1677s`.

Compared with current-failure fallback best, this checkpoint has `8` no-regression blockers and loses `cracked-star-jar` 300s win rate from `0.3333` to `0.0`. Compared with the seed63100 stage02 baseline, it has `5` blockers.

## Failure Analysis

`failure_analysis_300s.md` records `9` failures:

- `soda-creek`: `3` failures, with `1` opening failure and `2` late-window failures.
- `caramel-workshop`: `3` failures, with `1` opening failure and `2` late-window failures.
- `cracked-star-jar`: `3` failures, with `1` mid-window failure and `2` late-window failures.

Phase-specific multipliers are useful for probing, but this configuration still leaves opening argmax disagreement and mid-window KL drift unresolved. The next repair should avoid another global anchor pass and instead split the problem into an explicit opening freeze/wrapper plus a separate mid/late constrained repair target that is checked against current-failure best before any longer run.

## Artifacts

- `train_run.json`
- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_phase_specific_anchor_smoke.zip`
- `ppo_phase_specific_anchor_smoke_metadata.json`
- `anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_opening_aware_probe.md`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.md`
