# Demo buildcraft repair v16 candidates

本候选包只覆盖 `frosting-grassland-standard` 波次，用于验证 v15 failure case 指向的 210-300 秒路线压力问题。

v16 不修改正式内容池，不修改玩家武器、被动、敌人属性、Boss、地图或 Runtime。它只把 Boss 后窗口中一小部分高速 / 远程压力换成更慢、更容易读的压力，目标是让 GreedyXpBot 不再在 225-229 秒固定死亡，同时避免 Coward、Route、Kite 和 BossHunter 越过各自目标区间。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
