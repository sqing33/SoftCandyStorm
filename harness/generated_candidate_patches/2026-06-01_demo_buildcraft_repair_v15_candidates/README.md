# Demo Buildcraft Repair v15 Candidates

本候选批次继续修复 v14 剩余的 Greedy 低胜率问题。

v15 基于 repair v14 full pack，仍只作为 generated candidate。调整重点：

- 覆盖 `sprinkle-spitter` 与 `frosty-straw`。
- 把 `sprinkle-spitter` 的 XP / score 从 v14 的 6 / 18 回退到 v13 的 5 / 16。
- 把 `frosty-straw` 调整为轻量防御控制被动，增加 `defense` 标签、少量移动速度和小额生命。
- 目标是验证 Greedy 在 225-229 秒低血量升级窗口是否需要一个非输出生存选择。
- 不改 `frosting-grassland-standard` 的 v10 波次结构。
- 不改玩家武器、Boss、地图或正式内容池。

状态：generated candidate only，不能直接进入 accepted_content 或 Runtime 正式内容。
