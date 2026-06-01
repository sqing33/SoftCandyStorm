# Demo buildcraft repair v20 candidates

本候选包只覆盖 `frosting-grassland-standard` 波次，用于修复 v18 的 10 seed 扩样中 RouteBot 略高于目标区间的问题，并明确回避 v19 的 `sugar-moth` 侧翼替换方向。

v20 回到 v18 full pack 基线，只在 210-300 秒 Boss 后窗口做极窄压力换位：把 `sandwich-cookie-creep` 的 0.01 权重转给 `sprinkle-spitter`。临时 10 seed 探针显示该方向可把 Route 从 40% 拉回 30%，同时保住 Coward 的 10% 下限；Greedy 和 Kite 仍需要后续候选继续修复。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
