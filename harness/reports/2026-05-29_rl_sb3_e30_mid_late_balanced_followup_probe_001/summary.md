# SB3 E30 Mid-late Balanced Follow-up Probe

## 结论

- Decision: `sb3_e30_mid_late_balanced_followup_probe_rejected_parent_regression`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Model: `ppo_e30_mid_late_balanced_followup_probe.zip`
- Reward profile: `late-win-conversion`
- Training timesteps: `256`
- Anchor guard: `anchor_validation_guard_passed`
- Full anchor gate: `behavior_clone_anchor_alignment_within_thresholds`
- Window regression vs e30: `policy_window_regression_passed`
- Window regression vs mid-anchor parent: `policy_window_regression_failed`
- Repair probe gate: `rl_repair_probe_gate_failed`
- Failure case: `harness/failed_cases/fail_20260529_003_sb3_e30_mid_late_balanced_followup_parent_regression.json`

本 probe 从 `e30_mid_anchor_guarded_probe` parent 继续 `256` timestep，在保持 mid-window anchor 权重 `2.0` 的同时把 late-window anchor 权重从 `1.0` 提到 `1.5`，用于验证是否能保住中窗动作分布保护并恢复 300 秒转换信号。

结论是否定的。训练期 anchor guard 通过，top drift rows 和 full-anchor alignment 也通过；相对原始 e30 baseline 的 60 / 180 / 300 秒 no-regression 仍通过。但相对 parent mid-anchor 分支出现两个回归 blocker：`soda-creek` 180 秒平均存活下降 `6.857s`，`caramel-workshop` 300 秒平均存活下降 `5.19s`。`repair_probe_gate` 因此拒绝该分支。

300 秒 high-pressure 三图胜率仍全部为 `0.0`，没有找回上一轮 512 timestep probe 中 `cracked-star-jar` 的 `0.3333` 胜率信号。该结果说明“在 parent 上继续加 late 权重”会损伤已有 limited-followup 分支，下一步不应沿这条配置加长，而应改成显式 opening retention / late conversion 分离约束，或先设计能同时保留 parent 与 e30 的多基线门禁。

## Training And Guard

| Item | Value |
| --- | --- |
| Timesteps | `256` |
| Train maps | `high-pressure` |
| Train seeds | `63100-63102` |
| Learning rate | `0.00001` |
| Entropy coefficient | `0.02` |
| Anchor regularization weight | `2.0` |
| Anchor interval | `256` |
| Anchor epochs per interval | `2` |
| Anchor sample weighting | `map_time_bucket_balance` |
| Time bucket weights | `opening_lt_60=1.5`, `mid_60_to_180=2.0`, `late_180_to_300=1.5` |
| Anchor final mean KL | `0.106516` |
| Anchor final argmax agreement | `0.8255` |
| Final guard decision | `anchor_validation_guard_passed` |

## Anchor Alignment

| Scope | Samples | Mean KL | Argmax agreement | Decision |
| --- | ---: | ---: | ---: | --- |
| Top drift rows | `200` | `0.019612` | `0.955` | `behavior_clone_anchor_alignment_within_thresholds` |
| Full anchor + drift | `36626` | `0.103613` | `0.8311` | `behavior_clone_anchor_alignment_within_thresholds` |

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `180s` | `multimap_comparison_recorded_watch` | `0.3333` | `0.6667` | `0.6667` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.0` |

300 秒 failure analysis 仍记录 `9` 条失败：三张 high-pressure 地图各 `3` 条，且每张图都有 `1` 条 opening failure 与 `2` 条 late failure。`caramel-workshop` 300 秒 dominant action 变为 action `1`、ratio `0.4149`，说明 late 加权没有保住 parent 的长局动作分布。

## Window Regression

相对 e30 baseline：`policy_window_regression_passed`。

相对 mid-anchor parent：`policy_window_regression_failed`。

| Window | Map | Survival Δ | Dominant Ratio Δ | Blocker |
| --- | --- | ---: | ---: | --- |
| `180s` | `soda-creek` | `-6.857` | `0.0617` | `average_survival_seconds dropped 6.857s beyond allowed 5.0s` |
| `300s` | `caramel-workshop` | `-5.19` | `0.17` | `average_survival_seconds dropped 5.19s beyond allowed 5.0s` |

## 判断

- late-window 权重从 `1.0` 提到 `1.5` 没有恢复 300 秒胜率。
- 相对 e30 的 no-regression 通过不足以说明该分支可继续；与 parent mid-anchor 分支比较后，该配置已发生回归。
- 该分支不得作为下一轮 start model，也不得推进 RL acceptance 或 policy candidate。
- 下一步应把 parent-preservation 作为硬约束，优先设计多基线 repair gate 或显式分离 opening retention 与 late conversion，而不是继续加长本配置。

## 输出文件

- `ppo_training_report.json`
- `ppo_e30_mid_late_balanced_followup_probe.zip`
- `ppo_e30_mid_late_balanced_followup_probe_metadata.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `anchor_drift_alignment.json`
- `full_anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `window_regression_vs_e30.json`
- `window_regression_vs_e30.md`
- `window_regression_vs_mid_anchor_parent.json`
- `window_regression_vs_mid_anchor_parent.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
