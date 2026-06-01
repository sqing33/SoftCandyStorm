# Demo buildcraft repair v17 candidates

本候选包只覆盖 `frosting-grassland-standard` 波次，用于修复 v16 把 Greedy 与 Route 同时救得过强的问题。

v17 保留“减少远程 / 侧翼死亡窗口”的方向，但不继续增加基础软糖的安全比例。它把一部分 `sugar-moth` 和 `sprinkle-spitter` 压力转给 `sandwich-cookie-creep` 与 `sticky-bear-gummy`，让动态捡经验路线有更多可读空间，同时让固定路线仍面对慢速堵路和轻控制。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
