# Stage 02 Long-run Retention Probe

## 结论

- Gate decision: `long_run_retention_probe_rejected_mid_late_regression`
- Model: `ppo_long_run_retention_probe.zip`
- Warm start: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Failure case: `harness/failed_cases/fail_20260528_069_stage02_long_run_retention_probe_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验从 stage 02 PPO checkpoint 继续训练，使用 `long-run-retention` reward profile、`4096` timesteps、训练 seed `62800-62802,63100-63102`、learning rate `0.00002`、entropy coefficient `0.03`。目标是验证 retention reward 是否能保住 stage 02 的 60/180 秒行为，同时改善 300 秒长窗。

结果：probe 仍被拒绝，但比上一轮 `late-route-recovery` continuation 更接近可用。补录 `seed_start 63100` stage 02 baseline 后，同 seed no-regression 只剩 `1` 个 blocker：`cracked-star-jar` 300 秒平均存活低于 baseline `13.7463s`。60 秒三图全胜且无回归，180 秒三图无回归，300 秒 `soda-creek` 和 `caramel-workshop` 平均存活高于 baseline；但 300 秒三图仍全为 `0.0` 胜率，所以不能推进 stage 03 或 RL acceptance。

> 注：旧的 `window_regression_vs_stage02.md` 使用 stage 02 `seed_start 62800` baseline 与本 probe 的 `63100` 结果做跨 seed 摘要比较，只保留为历史诊断；严格判断以 `window_regression_vs_seed63100_stage02.md` 为准。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `1.0` | `0.6667` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | short-window retention preserved |
| `180s` | None | `0` | no same-seed regression |
| `300s` | `cracked-star-jar` | `1` | cracked survival regression |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `0` | none | short-window preserved |
| `180s` | `2` | soda mid `1`, cracked mid `1` | mid-window pressure deaths |
| `300s` | `9` | soda mid `1` / late `2`, caramel late `3`, cracked mid `1` / late `2` | long-window recovery still unresolved |

## 判断

- `long-run-retention` is a better direction than the previous short `late-route-recovery` continuation because it preserved all 60 秒 windows and reduces seed-matched no-regression blockers to `1`.
- It still cannot replace stage 02 as an accepted policy because 300 秒三图胜率仍全为 `0.0` and `cracked-star-jar` long-window survival regresses.
- Next repair should keep the retention objective but add map/window-specific constraints for `soda-creek` and `cracked-star-jar`, instead of promoting this checkpoint.

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_long_run_retention_probe.zip`
- `ppo_long_run_retention_probe_metadata.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_stage02.json`
- `window_regression_vs_stage02.md`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
