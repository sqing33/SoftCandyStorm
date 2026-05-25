# PPO Observation V2 高压地图 300 秒训练 50k 对比 001

日期：2026-05-26

## 目标

使用 observation v2、`high-pressure` 地图预设和 300 秒训练 episode 训练出的 50k PPO 模型，在三张高压地图上运行 10 seed / 300 秒 deterministic 评估，并与 Random/Kite/Tank 规则 Bot 做同 seed 对比。

## 结论

Gate 决策：`multimap_comparison_recorded_needs_policy_repair`

300 秒训练 episode 明显改善了长局存活，但没有修复高压地图泛化。与上一轮 observation v2 50k 多地图 random 模型相比：

- `soda-creek`：胜率从 0% 提升到 10%，平均存活从 33.6698 秒提升到 217.3437 秒。
- `caramel-workshop`：胜率仍为 0%，平均存活从 160.1878 秒提升到 209.3660 秒。
- `cracked-star-jar`：胜率从 0% 提升到 10%，平均存活从 56.5967 秒提升到 238.4666 秒。

这说明训练 episode 对齐 300 秒是有效方向，但该 policy 仍不能作为正式跨地图 RL 压力测试 Bot。

## 结果摘要

| Map | PPO Win Rate | 平均存活秒数 | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 | 规则 Bot 参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| soda-creek | 10% | 217.3437 | 119.9161 | 553.5 | 动作 8 = 54.57% | 0.4557 | Random 0%，Kite 10%，Tank 50% |
| caramel-workshop | 0% | 209.3660 | 120.2623 | 321.3 | 动作 8 = 60.91% | 0.4455 | Random 0%，Kite 40%，Tank 20% |
| cracked-star-jar | 10% | 238.4666 | 117.2084 | 543.6 | 动作 8 = 57.31% | 0.4367 | Random 0%，Kite 40%，Tank 50% |

## 通过项

- 每张地图的动作分布 gate 仍通过：最大动作占比低于 75%，归一化动作熵高于 0.25。
- 高压训练显著改善 `soda-creek` 与 `cracked-star-jar` 的早死问题。
- 聚合对比报告能一次输出 `summary.maps`、`repair_maps`、per-map policy/rule Bot 指标和 `multimap_comparison` gate。

## 失败项

- `caramel-workshop` 胜率仍为 0%。
- `soda-creek` 和 `cracked-star-jar` 胜率只有 10%，仍低于 TankBot 的 50%。
- 三张地图平均承伤都接近死亡阈值，说明 policy 仍无法稳定处理中后期压力。
- 动作偏好集中在 8/5/6，当前策略像是在固定朝左上/下侧逃生，缺少对 hazard、Boss 和波次节奏的条件化反应。

## Failure Case

- `harness/failed_cases/fail_20260526_014_ppo_high_pressure_train300_gap.json`

## 下一步

1. 不把该 50k high-pressure train300 PPO policy 推进为正式 RL 压力测试 Bot。
2. 下一轮优先做 reward shaping，而不是只继续拉长训练：加入 Boss/hazard/受伤前兆、低血量安全距离、地图边界和中后期存活质量相关奖励。
3. 继续保留 `--train-seconds 300` 和 `--train-map-preset high-pressure` 作为训练入口，但需要把 map-specific failure 反馈进 reward 或 curriculum。
4. 修复后重跑同一 `high-pressure` 10 seed / 300 秒聚合对比；通过后再扩回 `all-base-demo`。
