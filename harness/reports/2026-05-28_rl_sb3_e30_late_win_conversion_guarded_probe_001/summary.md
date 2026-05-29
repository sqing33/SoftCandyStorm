# SB3 E30 Late-win-conversion Guarded Probe

## 结论

- Decision: `sb3_e30_late_win_conversion_guarded_probe_rejected_repair_gate_failed`
- Start model: `harness/reports/2026-05-28_rl_sb3_supervised_realign_full_anchor_drift_w40_e30_001/ppo_supervised_realign_full_anchor_drift_w40_e30.zip`
- Model: `ppo_e30_late_win_conversion_guarded_probe.zip`
- Reward profile: `late-win-conversion`
- Training timesteps: `512`
- Anchor guard: `anchor_validation_guard_passed`
- Full anchor gate: `behavior_clone_anchor_alignment_within_thresholds`
- Repair probe gate: `rl_repair_probe_gate_failed`
- Failure case: `harness/failed_cases/fail_20260529_001_sb3_e30_late_win_conversion_guarded_probe_repair_gate.json`

本 probe 从 e30 supervised re-alignment checkpoint 出发，做一个很小的 `late-win-conversion` closed-loop continuation。训练使用 full-anchor + top drift rows 的离线 KL anchor，并启用 validation guard：`max_validation_kl = 0.25`、`min_argmax_agreement = 0.8`。guard 没有触发，说明这个起点比之前的 closed-loop anchor smoke 更稳定。

但该分支仍被拒绝。60 秒与 180 秒窗口相对 e30 有改善，300 秒也把 `cracked-star-jar` 恢复到 `0.3333` 胜率；但 `soda-creek` 与 `caramel-workshop` 300 秒仍为 `0.0`，且 `window_regression_vs_e30` 发现 `caramel-workshop` 180 秒 dominant action ratio 增加 `0.265`，超过 `0.2` 阈值。`repair_probe_gate` 因此输出 `rl_repair_probe_gate_failed`。

## Training And Guard

| Item | Value |
| --- | --- |
| Timesteps | `512` |
| Train maps | `high-pressure` |
| Train seeds | `63100-63102` |
| Learning rate | `0.00002` |
| Entropy coefficient | `0.02` |
| Anchor samples | `36626` |
| Anchor drift samples | `200` |
| Anchor final mean KL | `0.109673` |
| Anchor final argmax agreement | `0.8224` |
| Final guard decision | `anchor_validation_guard_passed` |

## Anchor Alignment

| Scope | Samples | Mean KL | Argmax agreement | Decision |
| --- | ---: | ---: | ---: | --- |
| Top drift rows | `200` | `0.020313` | `0.97` | `behavior_clone_anchor_alignment_within_thresholds` |
| Full anchor + drift | `36626` | `0.106657` | `0.8273` | `behavior_clone_anchor_alignment_within_thresholds` |

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `180s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.3333` |

300 秒 failure analysis 记录 `8` 条失败：`soda-creek` `3` 条、`caramel-workshop` `3` 条、`cracked-star-jar` `2` 条。失败仍覆盖 opening、mid 和 late，其中 `soda-creek` 三个时间桶各有一条失败，说明 long-run conversion 不是单纯 late-only 问题。

## Window Regression Vs E30

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
| --- | --- | ---: | ---: | ---: | --- |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `0.0153` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0173` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0804` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `38.2034` | `0.1631` | `pass` |
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.265` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.0527` | `pass` |
| `300s` | `soda-creek` | `0.0` | `8.1995` | `0.1991` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `4.3454` | `0.0562` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `90.0397` | `-0.079` | `pass` |

## 判断

- e30 checkpoint 是更好的 closed-loop 起点：训练期 guard 与离线 full-anchor alignment 都通过。
- 512 timestep `late-win-conversion` 产生有限正信号：短窗提升、`cracked-star-jar` 300 秒胜率恢复到 `0.3333`。
- 该分支仍不能推进：`soda-creek` / `caramel-workshop` 300 秒仍为 `0.0`，且 180 秒 `caramel-workshop` 出现 dominant action ratio regression。
- 下一步不应直接加长同配置；应先约束 `caramel-workshop` 180 秒动作分布，同时继续保留 e30 full-anchor alignment 和 300 秒 no-regression 作为硬门禁。

## 输出文件

- `ppo_training_report.json`
- `ppo_e30_late_win_conversion_guarded_probe.zip`
- `ppo_e30_late_win_conversion_guarded_probe_metadata.json`
- `anchor_drift_alignment.json`
- `full_anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `window_regression_vs_e30.json`
- `window_regression_vs_e30.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
