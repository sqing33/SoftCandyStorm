# Demo buildcraft repair v22 candidates

本候选包基于 `2026-06-01_demo_buildcraft_repair_v18_full_pack`，把 v21 探针中较有效的经济 / 召唤微调正式落成候选，并叠加 v20 中较有效的 Boss 后窗口波次调整。

v22 覆盖三项内容：

- `star-spoon`：拾取半径每级从 18 降到 17，降低 Greedy / Route 对远距离糖晶的安全转化。
- `pudding-turret`：每级冷却成长从 0.92 放缓到 0.935，削弱安全召唤成型后的无脑稳定性。
- `frosting-grassland-standard`：210-300 秒 Boss 后窗口把 `sandwich-cookie-creep` 权重从 0.17 降到 0.16，并把 `sprinkle-spitter` 从 0.07 提到 0.08，增加少量可读远程压力。

临时 300 秒 / 10 seed / all Bot 探针显示该方向能让 Coward、Kite、Tank、BossHunter、ZoneControl 和 Route 处在目标区间，但 Greedy 仍为 60.0%，略高于 25%-55% 目标上限。因此本批次只能作为 `repair` 证据，不得进入 accepted content。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
