# PPO 多地图扩样本对比 001

日期：2026-05-26

## 目标

使用新 Gym reward 下的 PPO 5000-step 模型，在全部 6 张 `base_demo` 地图上运行 10 seed、300 秒评估，并与 Random/Kite/Tank 规则 Bot 做同 seed 对比。

## 结论

Gate 决策：`repair`

PPO policy 没有复发单动作塌缩：6 张地图的最大动作占比均低于 75%，归一化动作熵均高于 0.25。但跨地图泛化不足，`soda-creek`、`caramel-workshop`、`cracked-star-jar` 的胜率分别只有 20%、20%、40%，且平均承伤约 99 到 119。该 policy 暂不能作为跨地图 RL 压力测试基线。

## 结果摘要

| Map | PPO Win Rate | 平均存活秒数 | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 | 规则 Bot 参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| frosting-grassland | 100% | 300.015 | 14.4543 | 526.5 | 动作 6 = 37.01% | 0.4985 | Kite/Tank 100%，Random 50% |
| soda-creek | 20% | 203.0071 | 118.8896 | 507.1 | 动作 2 = 49.79% | 0.4728 | Kite 60%，Tank 50%，Random 0% |
| cotton-cloud-pasture | 100% | 300.015 | 16.8997 | 558.1 | 动作 6 = 39.37% | 0.4948 | Kite/Tank 100%，Random 20% |
| caramel-workshop | 20% | 240.6718 | 116.3133 | 385.6 | 动作 2 = 42.05% | 0.4836 | Kite 50%，Tank 30%，Random 0% |
| jelly-platform | 100% | 300.015 | 37.9283 | 655.8 | 动作 2 = 39.73% | 0.4947 | Kite/Tank 100%，Random 20% |
| cracked-star-jar | 40% | 240.8562 | 99.7397 | 540.9 | 动作 2 = 46.66% | 0.4779 | Kite 80%，Tank 50%，Random 0% |

## 通过项

- 动作分布健康：所有地图最大动作占比均低于 75%。
- 动作熵健康：所有地图归一化动作熵均高于 0.25。
- 报告链路完整：每张地图都包含 policy summary、reward_breakdown、rule_bot_matrix 和 gate_decision。

## 失败项

- 跨地图泛化不足：PPO 在 3 张地图低于 50% 胜率，其中 `soda-creek` 与 `caramel-workshop` 只有 20%。
- 承伤偏高：失败地图平均承伤接近或超过 100。
- 训练覆盖不足：模型只来自当前单配置训练，尚未进行多地图训练或 curriculum。

## 下一步

1. 记录 RL failure case：PPO 多地图泛化不足。
2. 优先加入多地图训练或评估时地图随机化，再重跑同一 6 地图 10 seed / 300 秒矩阵。
3. 若多地图训练后仍稳定，再扩到 600 秒和更多 seed；在此之前不要把该 PPO 当作正式跨地图压力测试基线。
