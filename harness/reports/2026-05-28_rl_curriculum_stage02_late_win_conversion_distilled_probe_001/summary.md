# Stage 02 Late-win Conversion Distilled Probe

## 结论

- Gate decision: `late_win_conversion_distilled_probe_rejected_soda_regression`
- Teacher: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Distilled model: `ppo_distilled_from_current_failure_fallback.zip`
- Closed-loop model: `ppo_late_win_conversion_probe.zip`
- Failure case: `harness/failed_cases/fail_20260528_080_stage02_late_win_conversion_distilled_probe_regression.json`
- No-regression reports: `window_regression_vs_current_failure_best.md`, `window_regression_vs_seed63100_stage02.md`

本实验把 current-failure fallback best 的 behavior-clone teacher 蒸馏为 SB3 PPO 初始化，然后使用 `late-win-conversion` reward profile、high-pressure 三图随机训练、seed `63100-63105`、`2048` timesteps、learning rate `0.00002` 和 entropy coefficient `0.02` 做短 closed-loop 探针。目标是验证 240 秒后 final-minute win-conversion 信号能否在不破坏已有窗口的前提下改善 300 秒胜利转换。

结果：probe 被拒绝。蒸馏本身只是初始化证据，validation argmax accuracy 为 `0.7579`，target entropy 为 `1.136667`，不能作为 policy gate。续训后 60 秒 `soda-creek` 从 current best 的 `1.0` 回落到 `0.3333`，180 秒 `soda-creek` 回落到 `0.0`，300 秒仍为 `0.0/0.0/0.3333`。相对 current-failure fallback best 和 seed63100 stage02 baseline 均触发 `5` 个 no-regression blockers，不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

## Distillation

| Item | Value |
| --- | --- |
| Samples | `36426` |
| Teacher argmax agreement | `0.7771` |
| Teacher temperature | `1.25` |
| Uniform target mix | `0.02` |
| Target entropy | `1.136667` |
| Epochs | `3` |
| Final validation accuracy | `0.7579` |
| Final policy entropy | `1.422718` |

## Closed-loop Training

| Item | Value |
| --- | --- |
| Reward profile | `late-win-conversion` |
| Timesteps | `2048` |
| Train maps | `soda-creek`, `caramel-workshop`, `cracked-star-jar` |
| Train seeds | `63100-63105` |
| Learning rate | `0.00002` |
| Entropy coefficient | `0.02` |
| Warm start | `ppo_distilled_from_current_failure_fallback.zip` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.3333` | `1.0` | `1.0` | `multimap_comparison_recorded_watch` |
| `180s` | `0.0` | `1.0` | `1.0` | `multimap_comparison_recorded_needs_policy_repair` |
| `300s` | `0.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression

| Baseline | Decision | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| current-failure fallback best | `policy_window_regression_failed` | `5` | `soda-creek` 60/180 胜率和 60/180/300 平均存活回归 |
| seed63100 stage02 baseline | `policy_window_regression_failed` | `5` | `soda-creek` 60/180 胜率和 60/180/300 平均存活回归 |

## Failure Analysis

| Window | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `2` | soda opening `2` | distilled PPO early action `1` bias |
| `180s` | `3` | soda opening `2`, soda mid `1` | opening / mid retention broken before final-minute reward starts |
| `300s` | `8` | soda opening `2`, soda mid `1`, caramel late `3`, cracked late `2` | final-minute signal did not convert soda/caramel wins and broke soda retention |

## 判断

- `late-win-conversion` profile 入口可运行，但单独使用 final-minute reward 不能保护 earlier windows。
- 将 GRU/context fallback teacher 蒸馏成 memoryless SB3 `MlpPolicy` 后，`soda-creek` opening / mid 行为明显回归。
- 后续若继续 closed-loop 路线，应加入 explicit opening retention、staged opening protection、KL / behavior-clone anchor 或 per-map constraints；不要从该 checkpoint 继续推进。

## 输出文件

- `distill_run.json`
- `ppo_distilled_from_current_failure_fallback.zip`
- `ppo_distilled_from_current_failure_fallback_metadata.json`
- `train_run.json`
- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_late_win_conversion_probe.zip`
- `ppo_late_win_conversion_probe_metadata.json`
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
