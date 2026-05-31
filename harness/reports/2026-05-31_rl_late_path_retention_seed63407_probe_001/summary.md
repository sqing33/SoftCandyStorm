# Late Path Retention Seed 63407 Probe

## 目标

验证对 `caramel-workshop:63407` 从 `180s` 开始整段切回 e30 mid-anchor parent，是否足以恢复 selective opening guard 丢掉的 baseline 胜利路径。

## 配置

- Base policy：`harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Retention policy：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Target：`caramel-workshop:63407`
- Health-retention window：`180-300s`
- Pressure / low-health threshold：`0.0`
- Follow-up：single seed `63407`，`300s`

## 结果

| Seed | Baseline terminal | Candidate terminal | Survival |
|---:|---|---|---:|
| 63407 | duration_reached @ 300.0150s | player_health_depleted @ 235.6881s | 235.6881s |

Wrapper usage 为 `1670 / 7070` 次，`late_180_to_300` bucket 为 `100%` branch usage，但仍只把 selective opening guard 的 `231.0204s` 死亡推迟到 `235.6881s`。

## 结论

结论：`reject`。

从 `180s` 才切回 baseline-winning parent 仍然太晚，说明 `63407` 的胜利路径在 `60-180s` 中窗已经发生偏离。该结果不能作为 repair candidate，只能证明 late-only path retention 不足。

## 下一步

- 复查 `60-300s` mid-path retention，确认是否需要从 handoff / mid-window 就保护 baseline-winning route。
- 后续不要把 `180s` late-only retention 当作扩大矩阵的依据。
