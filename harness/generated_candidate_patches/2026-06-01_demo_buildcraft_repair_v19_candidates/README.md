# Demo buildcraft repair v19 candidates

本候选包只覆盖 `frosting-grassland-standard` 波次，用于修复 v18 通过 3 seed 但在 10 seed 扩样中过于安全的问题。

v19 保留 v18 的 `sprinkle-spitter` 权重，不继续增加高 XP 远程怪比例；它只在 210-300 秒 Boss 后窗口把 `bouncy-gummy` 的 0.02 安全权重转给 `sugar-moth`。目标是用更可读的侧翼压力压低 Greedy、Kite 和 Route 的扩样胜率，同时尽量保住 Coward 的 10% 下限。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
