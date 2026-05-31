# Health Retention Guard Seed 63407 Probe

## 目标

验证一个只在 `caramel-workshop:63407` late low-health 窗口触发的 evaluation-only health-retention guard，能否救回 selective opening guard 10 seed follow-up 丢掉的 baseline 胜利路径。

## 配置

- Base policy：`harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Retention policy：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Target：`caramel-workshop:63407`
- Health-retention window：`180-300s`
- Low-health threshold：`0.15`
- Follow-up：`caramel-workshop` seeds `63400-63409`，`300s`

## 结果

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| Win rate | 0.1 | 0.1 | 0.0 |
| Average survival seconds | 242.8409 | 238.65 | -4.1909 |
| Damage taken average | 115.8589 | 116.4336 | +0.5747 |
| Average kills | 387.7 | 380.2 | -7.5 |

`window_regression_caramel_300s_10seed.json` 判定为 `policy_window_regression_failed`，blocker 是 `300s/caramel-workshop` 平均存活下降 `4.1909s`。

Health-retention wrapper 在 10 seed follow-up 中只触发 `181 / 71589` 次，全部落在 `late_180_to_300`，但 seed `63407` 仍在 `231.0204s` 死亡，没有恢复 baseline 的 `300.0150s` 胜利。

## 结论

结论：`reject`。

低血量瞬时切回太晚。该探针没有改变 10 seed follow-up 的失败结论，也没有救回 `63407`。它只能作为诊断证据，说明 blocker 已经不是单纯 low-health recovery action，而是更早的 mid-path / route retention 偏离。

## 下一步

- 不再扩大 `180-300s` low-health-only guard。
- 用更早的 `60-300s` mid-path retention probe 复查 `63407` 是否依赖 60-180 秒路径保持。
- 后续任何 health-retention 组合仍必须跑 10 seed target follow-up 和 60 / 180 / 300 秒 high-pressure no-regression。
