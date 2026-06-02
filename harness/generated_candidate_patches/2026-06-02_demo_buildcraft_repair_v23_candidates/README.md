# Demo buildcraft repair v23 candidates

本候选包基于 `2026-06-02_demo_buildcraft_repair_v22_full_pack`，只覆盖 `frosting-grassland-standard` 一条糖霜草地波次。

v23 的目标不是新增内容，而是把 v22 的 300 秒 Demo 平衡继续收窄：v22 在 10 seed / all Bot 扩样中，除 `GreedyXpBot` 外均处于目标区间；`GreedyXpBot` 胜率为 60.0%，略高于 25%-55% 目标上限。

本批次调整：

- 210-255 秒：保留 v22 的 Boss 后窗口配置，继续给 Coward / Route / 低技能路线留恢复空间。
- 255-300 秒：单独拆出后段压力窗口，把 `sandwich-cookie-creep` 权重从 0.16 降到 0.15，并把 `sprinkle-spitter` 权重从 0.08 提到 0.09。

设计预期：

- 不削弱前期拾取经济，避免让低技能路线过早崩盘。
- 不大削 `rainbow-candy-shot` 或 `pudding-turret`，避免破坏五条 Demo 构筑路线。
- 只在 255 秒后增加少量可读远程压力，让已经成型的 Greedy 胜局需要继续走位，而不是靠安全拾取收益自然通关。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
