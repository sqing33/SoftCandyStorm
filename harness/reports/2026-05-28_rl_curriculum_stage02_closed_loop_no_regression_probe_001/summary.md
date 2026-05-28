# Stage 02 Closed-loop No-regression Probe

## 结论

- Gate decision: `closed_loop_no_regression_probe_rejected_window_regression`
- Model: `ppo_closed_loop_no_regression_probe.zip`
- Warm start: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Failure case: `harness/failed_cases/fail_20260528_068_stage02_closed_loop_no_regression_probe_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验从当前最佳 stage 02 PPO checkpoint 继续 closed-loop PPO 训练，使用 `late-route-recovery` reward profile、`2048` timesteps、训练 seed `62800-62802`，目标是验证回到 PPO 路线后是否能在不破坏 stage 02 短窗表现的前提下改善 300 秒长窗。

结果：probe 被拒绝。补录 `seed_start 63100` stage 02 baseline 后，同 seed no-regression 触发 `4` 个 blockers，主要集中在 `soda-creek`：60 秒胜率和平均存活回退，180/300 秒平均存活回退。300 秒三图仍为 `0.0/0.0/0.0`，不能推进 stage 03、不能作为 RL acceptance evidence。

> 注：旧的 `window_regression_vs_stage02.md` 使用 stage 02 `seed_start 62800` baseline 与本 probe 的 `63100` 结果做跨 seed 摘要比较，只保留为历史诊断；严格判断以 `window_regression_vs_seed63100_stage02.md` 为准。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | `soda-creek` | `2` | opening win rate and survival regression |
| `180s` | `soda-creek` | `1` | mid-window survival regression |
| `300s` | `soda-creek` | `1` | long-window survival regression |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `2` | soda opening `1`, caramel opening `1` | action `2` early failures |
| `180s` | `4` | soda opening `1` / mid `1`, caramel opening `1`, cracked mid `1` | action `2` / `7` mid failures |
| `300s` | `9` | soda opening `1` / mid `1` / late `1`, caramel opening `1` / late `2`, cracked mid `1` / late `2` | late route recovery remains unresolved |

## 判断

- Closed-loop PPO continuation did not preserve the stage 02 checkpoint behavior.
- The best current RL checkpoint remains stage 02 PPO, but it is still blocked by 300 秒 soda-creek / caramel-workshop `0.0` win rate and unresolved late-window failures.
- Next RL work should keep stage 02 as baseline and treat no-regression across `60s` / `180s` / `300s` as a hard precondition before any stage 03 or RL acceptance attempt.

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_closed_loop_no_regression_probe.zip`
- `ppo_closed_loop_no_regression_probe_metadata.json`
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
