# Mid Path Retention Seed 63407 Probe

## 目标

验证对 `caramel-workshop:63407` 从 `60s` 开始切回 e30 mid-anchor parent，是否能恢复 baseline-winning terminal path。

## 配置

- Base policy：`harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Retention policy：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Target：`caramel-workshop:63407`
- Health-retention window：`60-300s`
- Pressure / low-health threshold：`0.0`
- Follow-up：single seed `63407`，`300s`

## 结果

| Seed | Baseline terminal | Candidate terminal | Damage taken |
|---:|---|---|---:|
| 63407 | duration_reached @ 300.0150s | duration_reached @ 300.0150s | 74.1 |

Wrapper usage 为 `7199 / 9000` 次，`mid_60_to_180` 与 `late_180_to_300` bucket 都是 `100%` branch usage，opening bucket 不触发。该单 seed probe 成功恢复了 `63407` 的 baseline-winning path。

## 结论

结论：`repair`。

`63407` 的关键偏离发生在 `60-180s` 中窗，而不是 180 秒后的低血量瞬间。该结果是 repair evidence，不能单独作为 RL test Bot、stage 03 或 acceptance 证据。

## 下一步

- 扩大到 `caramel-workshop` seeds `63400-63409` 的 10 seed follow-up。
- 保留 60 / 180 / 300 秒 high-pressure no-regression，确认 target-specific mid-path guard 不污染已有短窗和跨图结果。
