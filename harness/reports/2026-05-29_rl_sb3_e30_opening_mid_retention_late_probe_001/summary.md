# SB3 E30 Opening/Mid Retention + Late Probe

## 结论

- Decision: `sb3_e30_opening_mid_retention_late_probe_rejected_multibaseline_regression`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Model: `ppo_e30_opening_mid_retention_late_probe.zip`
- Reward profile: `late-win-conversion`
- Training timesteps: requested `128`, actual `256`
- Anchor guard: `anchor_validation_guard_passed`
- Full anchor gate: `behavior_clone_anchor_alignment_within_thresholds`
- Window regression vs e30: `policy_window_regression_failed`
- Window regression vs mid-anchor parent: `policy_window_regression_failed`
- Repair probe gate: `rl_repair_probe_gate_failed`
- Failure case: `harness/failed_cases/fail_20260529_004_sb3_e30_opening_mid_retention_late_probe_regression.json`

本 probe 从 `e30_mid_anchor_guarded_probe` parent 重新出发，保持 `late-win-conversion` reward profile，但把 anchor time-bucket 权重改为 `opening_lt_60=2.0`、`mid_60_to_180=2.0`、`late_180_to_300=0.75`，目标是保留 opening/mid retention，并让 final-minute reward 自己推动 300 秒转换。

结果仍应拒绝。训练期 anchor guard 通过，drift-row 与 full-anchor alignment 都通过；300 秒 `cracked-star-jar` 胜率恢复到 `0.6667`，这是一个真实的 late conversion 信号。但 required multibaseline gate 失败：相对 e30 baseline 有 2 个 blocker，相对 mid-anchor parent 有 3 个 blocker，`repair_probe_gate` 合计记录 5 个 blockers。

## Training And Guard

| Item | Value |
| --- | --- |
| Requested timesteps | `128` |
| Actual timesteps | `256` |
| Train maps | `high-pressure` |
| Train seeds | `63100-63102` |
| Learning rate | `0.00001` |
| Entropy coefficient | `0.02` |
| Anchor regularization weight | `2.0` |
| Anchor interval | `128` |
| Anchor epochs per interval | `2` |
| Anchor sample weighting | `map_time_bucket_balance` |
| Time bucket weights | `opening_lt_60=2.0`, `mid_60_to_180=2.0`, `late_180_to_300=0.75` |
| Final guard decision | `anchor_validation_guard_passed` |

## Anchor Alignment

| Scope | Samples | Mean KL | Argmax agreement | Decision |
| --- | ---: | ---: | ---: | --- |
| Top drift rows | `200` | `0.019924` | `0.97` | `behavior_clone_anchor_alignment_within_thresholds` |
| Full anchor + drift | `36626` | `0.105559` | `0.8288` | `behavior_clone_anchor_alignment_within_thresholds` |

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `0.6667` |
| `180s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.6667` |

300 秒 failure analysis 记录 `7` 条失败：`soda-creek` 3 条、`caramel-workshop` 3 条、`cracked-star-jar` 1 条。`soda-creek` 失败横跨 opening / mid / late，`caramel-workshop` 仍偏 late failure，说明该配置没有解决多图共同稳定性。

## Window Regression

相对 e30 baseline：`policy_window_regression_failed`。

| Window | Map | Blocker |
| --- | --- | --- |
| `180s` | `caramel-workshop` | dominant action ratio +`0.2638` |
| `300s` | `soda-creek` | average survival -`24.3608s` |

相对 mid-anchor parent：`policy_window_regression_failed`。

| Window | Map | Blocker |
| --- | --- | --- |
| `180s` | `caramel-workshop` | dominant action ratio +`0.2413` |
| `300s` | `soda-creek` | average survival -`27.2947s` |
| `60s` | `cracked-star-jar` | win rate -`0.3333` |

## 判断

- 该 probe 找回了 `cracked-star-jar` 300 秒转换信号，但代价是多基线回归，不可继续加长。
- opening/mid 强 anchor + late 弱 anchor 不能把 final-minute conversion 与 retention 解耦。
- 下一步应考虑 per-map late conversion、split-policy evaluation，或更细粒度的 action-distribution guard；不能从该 checkpoint 继续，也不能推进 RL acceptance 或 policy candidate。

## 输出文件

- `ppo_training_report.json`
- `ppo_e30_opening_mid_retention_late_probe.zip`
- `ppo_e30_opening_mid_retention_late_probe_metadata.json`
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
