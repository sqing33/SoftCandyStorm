# Stage 02 Map-Bucket Anchor Full Smoke

## 结论

- Gate decision: `policy_window_regression_failed`
- Model: `ppo_anchor_map_bucket_full_smoke.zip`
- Start model: `../2026-05-28_rl_curriculum_stage02_opening_aware_late_win_conversion_probe_001/ppo_distilled_opening_aware.zip`
- Anchor fallback: `../2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening: `../2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Training: `1024` PPO timesteps, `late-win-conversion`, `learning_rate=2e-05`, `ent_coef=0.02`
- Anchor regularization: full `36426` samples, `map_time_bucket_balance`, `weight=2.0`, `512` timestep interval, `2` KL epochs per interval
- Failure case: `fail_20260528_083`

本报告验证 full-dataset + map/time-bucket anchor KL 约束是否能修复上一轮 anchor-regularized PPO 的全量 alignment 漂移。结果仍失败，不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

训练内 final validation 为 mean KL `0.330579`、argmax agreement `0.692`，没有达到诊断阈值。全量 anchor alignment 也失败：overall mean KL `0.332669`，overall argmax agreement `0.6977`。相对上一轮 `8192` 样本 smoke，opening bucket mean KL 从 `0.335834` 降到 `0.25152`，但 opening argmax agreement 仍只有 `0.5343`；mid `60-180s` mean KL 仍为 `0.420859`，argmax agreement `0.6539`。

## Fixed Windows

| Window | Soda Creek | Caramel Workshop | Cracked Star Jar | Decision |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `0.6667` | `0.6667` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

Compared with the immediately previous opening-aware PPO probe, this run still has `1` no-regression blocker: `caramel-workshop` 300s average survival drops by `2.456s`.

Compared with current-failure fallback best, this checkpoint has `8` no-regression blockers and loses `cracked-star-jar` 300s win rate from `0.3333` to `0.0`. Compared with the seed63100 stage02 baseline, it still has `4` blockers.

## Failure Analysis

`failure_analysis_300s.md` records `9` failures:

- `soda-creek`: `3` failures, with `1` opening failure and `2` late-window failures.
- `caramel-workshop`: `3` failures, with `1` opening failure and `2` late-window failures.
- `cracked-star-jar`: `3` failures, with `1` mid-window failure and `2` late-window failures.

The map/time-bucket weighting improved opening KL but shifted more deterministic mass toward action `7` in mid/late windows and removed the previous cracked-star-jar 300s win. The next repair should not increase global anchor weight again. It should split the anchor objective by phase, freeze or wrap opening explicitly, and apply a separate mid/late constrained repair objective instead of one global KL pass.

## Artifacts

- `train_run.json`
- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_anchor_map_bucket_full_smoke.zip`
- `ppo_anchor_map_bucket_full_smoke_metadata.json`
- `anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_opening_aware_probe.md`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.md`
