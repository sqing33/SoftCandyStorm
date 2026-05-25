# PPO Observation V2 多地图对比 001

日期：2026-05-26

## 目标

复用 observation v2 的 10000-step PPO 多地图 random 训练模型，在全部 6 张 `base_demo` 地图上运行 10 seed、300 秒 deterministic 评估，并与 Random/Kite/Tank 规则 Bot 做同 seed 对比，确认 v2 短训模型是否已经具备跨地图泛化能力。

## 结论

Gate 决策：`repair`

v2 PPO policy 没有触发内置 action-bias repair：所有地图最大动作占比低于 75%，归一化动作熵高于 0.25。但 300 秒跨地图泛化仍失败：`soda-creek`、`caramel-workshop`、`cracked-star-jar` 胜率均为 0%，`jelly-platform` 胜率也只有 30%，高压地图平均承伤接近或超过 120。该 10k v2 policy 不能作为正式跨地图 RL 压力测试基线。

`compare-rule-bots` 报告自身的 `gate_decision` 只检查 action bias；本 summary 的 `repair` 是基于跨地图胜率、承伤、击杀和规则 Bot 参考做出的 Harness 结论。

## 结果摘要

| Map | PPO Win Rate | 平均存活秒数 | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 | Mean Top Actions | 规则 Bot 参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| frosting-grassland | 70% | 276.9594 | 95.6088 | 470.6 | 动作 1 = 73.73% | 0.3737 | 1 = 0.2322, 4 = 0.1616, 0 = 0.1277 | Random 70%，Kite 90%，Tank 100% |
| soda-creek | 0% | 89.8302 | 120.3078 | 163.9 | 动作 1 = 38.21% | 0.5922 | 1 = 0.1627, 4 = 0.1602, 0 = 0.1543 | Random 0%，Kite 10%，Tank 50% |
| cotton-cloud-pasture | 60% | 272.7058 | 91.8935 | 483.7 | 动作 1 = 71.92% | 0.3875 | 1 = 0.2312, 4 = 0.1613, 0 = 0.1302 | Random 20%，Kite/Tank 100% |
| caramel-workshop | 0% | 179.6434 | 120.5901 | 273.8 | 动作 1 = 54.82% | 0.5098 | 1 = 0.1984, 4 = 0.1634, 0 = 0.1478 | Random 0%，Kite 40%，Tank 20% |
| jelly-platform | 30% | 209.0309 | 113.5097 | 422.6 | 动作 1 = 54.85% | 0.5074 | 1 = 0.1962, 4 = 0.1603, 0 = 0.1455 | Random 0%，Kite/Tank 100% |
| cracked-star-jar | 0% | 110.0006 | 120.4891 | 189.5 | 动作 1 = 43.60% | 0.5714 | 1 = 0.1735, 4 = 0.1597, 0 = 0.1519 | Random 0%，Kite 40%，Tank 50% |

## 通过项

- 动作分布 gate 通过：所有地图最大动作占比低于 75%。
- 动作熵 gate 通过：所有地图归一化动作熵高于 0.25。
- 报告链路完整：每张地图都包含 policy summary、action_score_diagnostic、rule_bot_matrix、findings 和 rule_bot_command。

## 失败项

- 跨地图胜率不足：4 张地图低于 50%，其中 3 张地图为 0%。
- 承伤偏高：`soda-creek`、`caramel-workshop`、`cracked-star-jar` 平均承伤约 120，`jelly-platform` 也超过 113。
- 10k 训练仍偏短：v2 修复了 60 秒短局动作 gate，但没有形成 300 秒中后期、Boss 和 hazard 规避策略。
- 动作偏好仍单一：全部地图的 mean top action 都是动作 1，说明策略仍学到一条主移动倾向。

## Failure Case

- `harness/failed_cases/fail_20260526_012_ppo_observation_v2_multimap_gap.json`

## 下一步

1. 不把该 10k v2 PPO policy 推进为正式 RL 压力测试 Bot。
2. 下一轮应增加训练规模，优先尝试 50000 或 100000 requested timesteps 的 observation v2 多地图训练。
3. 若长训仍失败，再加入 300 秒训练 episode、curriculum、高压地图定向训练或 Boss/hazard reward shaping。
4. 修复后必须重跑同一 6 地图 10 seed / 300 秒 deterministic 对比。
