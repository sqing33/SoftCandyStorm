# Terminal Sequence Selective Opening Guard Probe

## 目标

验证 `terminal-sequence-recovery` checkpoint 能否在保留 300 秒 caramel 转胜信号的同时，通过定向 opening guard 避免 60 秒 `caramel-workshop` 回归。

## 配置

- Baseline：`harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_comparison_{60s,180s,300s}.json`
- Candidate model：`harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Opening guard：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Opening target：`caramel-workshop:63400`
- Opening window：`60s`
- Edge branch：`soda-creek:0-60s`、`caramel-workshop:30-45s`
- Late safety：all-map `late_recovery_filter` from `60s`
- Seed window：`63400-63402`

## 结果

| Window | soda-creek | caramel-workshop | cracked-star-jar |
|---|---:|---:|---:|
| 60s win rate | 1.0 | 1.0 | 1.0 |
| 180s win rate | 1.0 | 1.0 | 1.0 |
| 300s win rate | 1.0 | 0.3333 | 1.0 |

相对 per-map edge branch + all-map late filter baseline，300 秒窗口没有新增回归：

- `soda-creek`：胜率保持 `1.0`，平均存活保持 `300.015s`
- `caramel-workshop`：胜率 `0.0 -> 0.3333`，平均存活 `+17.0636s`
- `cracked-star-jar`：胜率 `0.3333 -> 1.0`，平均存活 `+10.2753s`

`window_regression_vs_per_map_chain` 判定为 `policy_window_regression_passed`，blockers 为 `0`。

## 结论

结论：`repair`。

定向 opening guard 首次把 terminal-sequence checkpoint 的 300 秒 conversion 收益与 60 / 180 / 300 秒 high-pressure no-regression 同时保住。该结果只能作为 repair evidence 和后续 limited follow-up 输入，不能作为 RL test Bot、stage 03、玩法平衡或 acceptance 证据。

本探针不是 `terminal_conversion_branch` 分派，因此不适用要求 branch usage 的 `terminal_conversion_probe_gate`。后续如果重新走 terminal branch 路线，仍必须单独通过 terminal branch usage、目标窗口转胜和 no-regression 的 gate。

## 下一步

- 扩大到更多 seed，优先做 `caramel-workshop` 300 秒 target follow-up。
- 对仍失败的两条 caramel seed 保存 trace，确认剩余 blocker 是低血量 / hazard conversion 还是 opening debt。
- 保留当前 per-map edge branch + all-map late filter 作为 baseline，继续要求 60 / 180 / 300 秒 no-regression。
