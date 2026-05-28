# Stage 02 Anchor-Regularized PPO Smoke

## 结论

- Gate decision: `policy_window_regression_failed`
- Model: `ppo_anchor_regularized_smoke.zip`
- Start model: `../2026-05-28_rl_curriculum_stage02_opening_aware_late_win_conversion_probe_001/ppo_distilled_opening_aware.zip`
- Anchor fallback: `../2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening: `../2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Training: `1024` PPO timesteps, `late-win-conversion`, `learning_rate=2e-05`, `ent_coef=0.02`
- Anchor regularization: `8192` limited samples, `512` timestep interval, `1` KL epoch per interval
- Failure case: `fail_20260528_082`

本报告验证 `train_sb3.py --anchor-model --anchor-dataset` 的真实训练路径。它不是 RL acceptance，也不是 stage 03 许可。目标是确认 closed-loop PPO 能在每个 chunk 后被 behavior-clone/opening anchor 拉回，并观察这种约束是否减少上一轮 opening-aware PPO 的窗口回归。

结果：有改善，但仍失败。训练内 `anchor_regularization.final_validation.mean_kl` 为 `0.265304`，`argmax_agreement` 为 `0.8462`；但在全量 `36426` 样本 anchor alignment 上，overall mean KL 仍为 `0.346885`，高于阈值 `0.25`，overall argmax agreement 为 `0.7044`，低于阈值 `0.75`。其中 `opening_lt_60` argmax agreement 只有 `0.4388`，`mid_60_to_180` mean KL 仍达 `0.421839`。

## Fixed Windows

| Window | Soda Creek | Caramel Workshop | Cracked Star Jar | Decision |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `0.6667` | `0.6667` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

Compared with the immediately previous opening-aware late-win-conversion PPO probe, this run preserves all 60s windows, improves `soda-creek` 180s from `0.3333` to `0.6667`, and restores `cracked-star-jar` 300s from `0.0` to `0.3333`. The validator still reports one blocker: `caramel-workshop` 300s average survival drops by `3.0339s`.

Compared with current-failure fallback best, this checkpoint still has `7` no-regression blockers. Compared with the seed63100 stage02 baseline, it still has `4` blockers. The hard blocker remains: `soda-creek` and `caramel-workshop` are still `0.0` win rate at 300s.

## Failure Analysis

`failure_analysis_300s.md` records `8` failures:

- `soda-creek`: `3` failures, with `1` opening failure and `2` late-window failures.
- `caramel-workshop`: `3` failures, with `1` opening failure and `2` late-window failures.
- `cracked-star-jar`: `2` failures, one mid-window and one late-window.

The candidate has healthier action distribution than the original opening-aware PPO, but the remaining failures are still mixed opening + late-window survival failures. The next repair should not simply increase PPO timesteps. Stronger per-window anchor sampling, explicit full-dataset KL weight, or per-map constrained repair is needed before another no-regression probe.

## Artifacts

- `train_run.json`
- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_anchor_regularized_smoke.zip`
- `ppo_anchor_regularized_smoke_metadata.json`
- `anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_opening_aware_probe.md`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.md`
