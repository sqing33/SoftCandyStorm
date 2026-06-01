# Demo buildcraft repair v18 candidates

本候选包只覆盖 `frosting-grassland-standard` 波次，用于修复 v17 中 Greedy 仍略高于目标区间的问题。

v18 保留 v17 的慢速阻挡回填方向，只在 210-300 秒 Boss 后窗口做极窄加压：把 `sandwich-cookie-creep` 的 0.01 权重还给 `sprinkle-spitter`。目标是让动态捡经验路线从 2/3 胜降到 1/3 胜，同时尽量保持固定路线 Bot 的 1/3 胜率。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
