# Demo Buildcraft Repair v7 Candidates

本候选批次修复 v6 在 300 秒 / 3 seed 烟测中暴露的过度修正问题。

v7 基于 repair v6 full pack，仍只作为 generated candidate。调整重点：

- 恢复 `bubble-shoes` 的每级移速收益，避免 BossHunter 和普通移动手感被 v6 牵连。
- 降低 `sprinkle-spitter` 的 XP 回报，并把弹幕压力调回可读区间，避免 Greedy / Kite 把压力怪转化为经济滚雪球。
- 保留 `caramel-sticky-ground` 的 v6 区域控制收益，继续支撑 ZoneControl。
- 将 `frosting-grassland-standard` 的 210-300 秒远程压力权重回落到 v5 与 v6 之间。

状态：generated candidate only，不能直接进入 accepted_content 或 Runtime 正式内容。
