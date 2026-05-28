# Stage 02 Opening-aware Late-win Conversion Probe

## 结论

- Gate decision: `opening_aware_late_win_conversion_probe_rejected_window_regression`
- Fallback teacher: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Opening teacher: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Distilled model: `ppo_distilled_opening_aware.zip`
- Closed-loop model: `ppo_opening_aware_late_win_conversion_probe.zip`
- Failure case: `harness/failed_cases/fail_20260528_081_stage02_opening_aware_late_win_conversion_regression.json`
- No-regression reports: `window_regression_vs_current_failure_best.md`, `window_regression_vs_seed63100_stage02.md`

本实验在上一轮 `late-win-conversion` 蒸馏失败后，改用 opening-aware teacher：样本 `time_seconds < 60` 时读取 SB3 stage 02 opening policy 概率，60 秒后回到 current-failure fallback behavior-clone teacher。随后仍使用 `late-win-conversion` reward profile、high-pressure 三图随机训练、seed `63100-63105`、`2048` timesteps、learning rate `0.00002` 和 entropy coefficient `0.02` 做短 closed-loop 探针。

结果：probe 被拒绝。opening-aware 蒸馏把 target entropy 提到 `1.210598`，续训后动作熵也更健康，但 60 秒 `soda-creek` 仍从 current best 的 `1.0` 回落到 `0.6667`，300 秒三图仍全部 `0.0` 胜率。相对 current-failure fallback best 触发 `8` 个 no-regression blockers；相对 seed63100 stage02 baseline 触发 `4` 个 blockers。该 checkpoint 不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

## Distillation

| Item | Value |
| --- | --- |
| Samples | `36426` |
| Opening seconds | `60.0` |
| Teacher argmax agreement | `0.6856` |
| Teacher temperature | `1.25` |
| Uniform target mix | `0.02` |
| Target entropy | `1.210598` |
| Epochs | `3` |
| Final validation accuracy | `0.6944` |
| Final policy entropy | `1.519551` |

## Closed-loop Training

| Item | Value |
| --- | --- |
| Reward profile | `late-win-conversion` |
| Timesteps | `2048` |
| Train maps | `soda-creek`, `caramel-workshop`, `cracked-star-jar` |
| Train seeds | `63100-63105` |
| Learning rate | `0.00002` |
| Entropy coefficient | `0.02` |
| Warm start | `ppo_distilled_opening_aware.zip` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression

| Baseline | Decision | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| current-failure fallback best | `policy_window_regression_failed` | `8` | `soda-creek` 60 秒胜率回归，180/300 秒多图平均存活回归，`cracked-star-jar` 丢失 300 秒胜利 |
| seed63100 stage02 baseline | `policy_window_regression_failed` | `4` | `soda-creek` 60 秒胜率和平均存活回归，`cracked-star-jar` 180/300 秒平均存活回归 |

## Failure Analysis

| Window | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `2` | soda opening `1`, caramel opening `1` | opening-aware 蒸馏仍未完全保住 seed `63101` 早期避险 |
| `180s` | `4` | soda opening `1`, soda mid `1`, caramel opening `1`, cracked mid `1` | 中窗恢复仍不稳定，尤其 `soda-creek` 与 `cracked-star-jar` |
| `300s` | `9` | opening `2`, mid `1`, late `6` | final-minute reward 没有转化胜利，三图 late failures 仍存在 |

## 判断

- opening-aware distillation 修正了上一轮 fallback-only teacher 的建模错误，但它本身仍只是初始化工具。
- 该策略的动作分布更分散，300 秒平均存活也有部分提高，但没有转化为任何 300 秒胜利。
- 与 current-failure fallback best 相比，本轮还丢掉了 `cracked-star-jar` 300 秒 `0.3333` 胜率，因此不能作为新的 retention anchor。
- 下一步不应继续从该 checkpoint 推进；应考虑 KL / behavior-clone anchor、per-map constrained repair，或显式保留 current-failure fallback best 的 300 秒 cracked retention。

## 输出文件

- `distill_run.json`
- `ppo_distilled_opening_aware.zip`
- `ppo_distilled_opening_aware_metadata.json`
- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_opening_aware_late_win_conversion_probe.zip`
- `ppo_opening_aware_late_win_conversion_probe_metadata.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_current_failure_best.json`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
