# Demo Buildcraft Repair v8 Candidates

本候选批次修复 v7 在 300 秒 / 3 seed 烟测中暴露的混合回归问题。

v8 基于 repair v7 full pack，仍只作为 generated candidate。调整重点：

- 保留 `bubble-shoes` 的恢复值，继续保护移动手感。
- 维持 `sprinkle-spitter` 低 XP，并把 210-300 秒远程压力作为不喂经济的可读挑战。
- 将 `caramel-sticky-ground` 从 v6 强度降到 v5/v6 中间值，避免 ZoneControl 超标。
- 把 `frosting-grassland-standard` 的 90-210 秒开局节奏回调到 v5，救回 Coward / BossHunter 的早中期稳定性。
- 小幅降低 `candy-crystal-lens` 的 XP 乘区，压住 Greedy 的滚雪球。

状态：generated candidate only，不能直接进入 accepted_content 或 Runtime 正式内容。
