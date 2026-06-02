# Demo buildcraft repair v24 candidates

本候选包基于 `2026-06-02_demo_buildcraft_repair_v23_full_pack`，只覆盖 `frosting-grassland-standard` 一条糖霜草地波次。

v23 已证明 255-300 秒的 0.01 远程压力换位太晚、太轻，无法改变 GreedyXpBot 的六个 300 秒胜局。v24 把同样的窄压力从 255 秒提前到 225 秒：

- 210-225 秒：保留 v22 / v23 的 Boss 后恢复窗口。
- 225-300 秒：把 `sandwich-cookie-creep` 权重从 0.16 降到 0.15，并把 `sprinkle-spitter` 权重从 0.08 提到 0.09。

设计预期：

- 让 Greedy 在 225-255 秒关键成型窗口继续处理可读远程压力。
- 不削弱 `rainbow-candy-shot`、`pudding-turret`、早期拾取经济或基础移动手感。
- 不使用 `sugar-moth` 替换基础权重，避免复现 v19 对 Coward / Route 的回归。

候选仍必须经过局部候选校验、物化、full pack 预检、静态预算、Schema contract、GameCore `validate-content`、隔离 `validate-candidates`、Bot 矩阵、Replay 回归和人工审查后，才可能进入后续阶段。
