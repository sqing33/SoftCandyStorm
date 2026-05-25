# PPO Observation V2 50k 多地图对比 001

日期：2026-05-26

## 目标

复用 observation v2 的 50000-step PPO 多地图 random 训练模型，在全部 6 张 `base_demo` 地图上运行 10 seed、300 秒 deterministic 评估，并与 Random/Kite/Tank 规则 Bot 做同 seed 对比，确认更长训练是否修复 10k v2 policy 的跨地图泛化失败。

## 结论

Gate 决策：`repair`

50k v2 PPO policy 的动作分布很健康，但跨地图泛化仍失败：`soda-creek`、`caramel-workshop`、`cracked-star-jar` 胜率均为 0%，`jelly-platform` 只有 30%。与 10k v2 相比，`frosting-grassland` 和 `cotton-cloud-pasture` 提升到 100%，但高压地图没有恢复，`soda-creek` 和 `cracked-star-jar` 的平均存活秒数反而明显下降。该模型不能作为正式跨地图 RL 压力测试基线。

`compare-rule-bots` 报告自身的 `gate_decision` 只检查 action bias；本 summary 的 `repair` 是基于跨地图胜率、存活、承伤、击杀和规则 Bot 参考做出的 Harness 结论。

## 结果摘要

| Map | PPO Win Rate | 平均存活秒数 | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 | Mean Top Actions | 规则 Bot 参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| frosting-grassland | 100% | 300.015 | 66.0451 | 525.8 | 动作 0 = 33.31% | 0.7629 | 4 = 0.1435, 1 = 0.1418, 3 = 0.1277 | Random 70%，Kite 90%，Tank 100% |
| soda-creek | 0% | 33.6698 | 120.3780 | 32.0 | 动作 4 = 66.97% | 0.4430 | 4 = 0.2571, 3 = 0.1542, 1 = 0.1498 | Random 0%，Kite 10%，Tank 50% |
| cotton-cloud-pasture | 100% | 300.015 | 46.4780 | 556.9 | 动作 0 = 35.25% | 0.7627 | 4 = 0.1370, 1 = 0.1321, 3 = 0.1302 | Random 20%，Kite/Tank 100% |
| caramel-workshop | 0% | 160.1878 | 120.5414 | 233.2 | 动作 0 = 48.48% | 0.6587 | 0 = 0.1647, 4 = 0.1312, 1 = 0.1286 | Random 0%，Kite 40%，Tank 20% |
| jelly-platform | 30% | 216.6418 | 110.2992 | 437.5 | 动作 0 = 37.52% | 0.7228 | 4 = 0.1443, 3 = 0.1305, 1 = 0.1284 | Random 0%，Kite/Tank 100% |
| cracked-star-jar | 0% | 56.5967 | 120.3107 | 75.8 | 动作 4 = 45.92% | 0.5758 | 4 = 0.1887, 3 = 0.1372, 1 = 0.1294 | Random 0%，Kite 40%，Tank 50% |

## 通过项

- 动作分布 gate 通过：所有地图最大动作占比低于 75%。
- 动作熵 gate 通过：所有地图归一化动作熵高于 0.25。
- `frosting-grassland` 与 `cotton-cloud-pasture` 达到 100% 胜率。
- 报告链路完整：每张地图都包含 policy summary、action_score_diagnostic、rule_bot_matrix、findings 和 rule_bot_command。

## 失败项

- 高压地图仍失败：`soda-creek`、`caramel-workshop`、`cracked-star-jar` 胜率均为 0%。
- 早死问题明显：`soda-creek` 平均存活 33.6698 秒，`cracked-star-jar` 平均存活 56.5967 秒。
- 承伤偏高：失败地图平均承伤约 120，基本接近死亡阈值。
- 动作分布已经足够分散，继续只提高 entropy 或重复动作惩罚很可能不是主解。

## Failure Case

- `harness/failed_cases/fail_20260526_013_ppo_observation_v2_50k_multimap_gap.json`

## 下一步

1. 不把该 50k v2 PPO policy 推进为正式 RL 压力测试 Bot。
2. 下一步优先改训练目标，而不是只继续拉长普通 60/180 秒训练：尝试 300 秒训练 episode、地图 curriculum 或高压地图定向训练。
3. 增加 Boss/hazard/受伤前兆 reward shaping，并关注 `soda-creek` 与 `cracked-star-jar` 的早死样本。
4. 修复后必须重跑同一 6 地图 10 seed / 300 秒 deterministic 对比。
