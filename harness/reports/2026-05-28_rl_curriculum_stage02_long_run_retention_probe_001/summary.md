# Stage 02 Long-run Retention Probe

## 结论

- Gate decision: `long_run_retention_probe_rejected_mid_late_regression`
- Model: `ppo_long_run_retention_probe.zip`
- Warm start: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Failure case: `harness/failed_cases/fail_20260528_069_stage02_long_run_retention_probe_regression.json`
- No-regression report: `window_regression_vs_stage02.md`

本实验从 stage 02 PPO checkpoint 继续训练，使用 `long-run-retention` reward profile、`4096` timesteps、训练 seed `62800-62802,63100-63102`、learning rate `0.00002`、entropy coefficient `0.03`。目标是验证 retention reward 是否能保住 stage 02 的 60/180 秒行为，同时改善 300 秒长窗。

结果：probe 仍被拒绝，但比上一轮 `late-route-recovery` continuation 更接近可用。60 秒三图全胜且相对 stage 02 baseline 无回归；180 秒保住 `caramel-workshop`，但 `soda-creek` 平均存活回退 `18.8349s`，`cracked-star-jar` 胜率和平均存活回退；300 秒三图仍为 `0.0/0.0/0.0`，并且 `cracked-star-jar` 从 stage 02 baseline 的 `0.3333` 胜率回退到 `0.0`。

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
| `180s` | `soda-creek`, `cracked-star-jar` | `3` | mid-window survival / cracked win regression |
| `300s` | `soda-creek`, `cracked-star-jar` | `3` | long-window survival / cracked win regression |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `0` | none | short-window preserved |
| `180s` | `2` | soda mid `1`, cracked mid `1` | mid-window pressure deaths |
| `300s` | `9` | soda mid `1` / late `2`, caramel late `3`, cracked mid `1` / late `2` | long-window recovery still unresolved |

## 判断

- `long-run-retention` is a better direction than the previous short `late-route-recovery` continuation because it preserved all 60 秒 windows and reduced no-regression blockers from `14` to `6`.
- It still cannot replace stage 02 as the baseline because it regresses `cracked-star-jar` 180/300 秒 and `soda-creek` survival.
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
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
