# Demo buildcraft repair v25 candidates

本候选包基于 `2026-06-02_demo_buildcraft_repair_v24_full_pack`，只覆盖 `pudding-turret` 一个召唤武器。

v24 已证明继续平移 210-300 秒 Boss 后窗口的 0.01 波次权重不足以改变 GreedyXpBot 的六个胜局。v25 改为处理后段安全构筑收益：Greedy 的 `70001` 与 `70003` 胜局都在彩虹糖弹满级后接入高等级布丁炮台，并用自动火力稳定跨过 225-300 秒压力段；Coward 的两个胜局不依赖布丁炮台，因此该修复比全局波次加压更窄。

调整内容：

- `pudding-turret` 版本提升到 6。
- 每级伤害成长从 `3` 降到 `2.5`。
- 每级冷却倍率从 `0.935` 放缓到 `0.94`。
- 不修改 `rainbow-candy-shot`、`star-spoon`、早期拾取经济、基础移动手感或糖霜草地波次。

设计预期：

- 保留召唤流的区域经营体验。
- 降低满级布丁炮台对安全成型 Greedy 构筑的自动清场收益。
- 尽量不影响 Coward 的低技能恢复下限、Route 的目标区间和 Kite/BossHunter 的高技能目标区间。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
