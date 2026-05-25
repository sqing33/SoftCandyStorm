# PPO Observation V2 50k 训练 001

日期：2026-05-26

## 目标

Observation v2 的 10k PPO 通过了 60 秒动作分布 gate，但 300 秒跨地图泛化失败。本轮将训练规模提高到 50000 requested timesteps，验证更长训练是否继续保持健康动作分布，并为下一轮 6 地图 300 秒对比准备候选模型。

## 训练配置

- Algorithm: `ppo`
- Observation version: `2`
- Observation length: `145`
- Requested timesteps: 50000
- Actual timesteps: 50176
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Entropy coefficient: `0.02`
- Training evaluation policy: `deterministic`
- Paired diagnostic policy: `stochastic`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_rule_bot_comparison`

50k v2 PPO 确定性评估动作分布进一步健康化：最大动作为动作 0，占比 31.91%，归一化动作熵为 0.7418。随机采样评估最大动作占比 16.01%，归一化动作熵为 0.9803，平均承伤为 0。

该模型已经具备进入 6 地图 10 seed / 300 秒 deterministic 规则 Bot 对比的资格。但 60 秒短局不能证明跨地图长局泛化，尤其 deterministic 平均承伤为 40.3，高于 10k v2 短局，需要在长局中复核。

## 关键指标

| 指标 | 10k Deterministic | 50k Deterministic | 50k Stochastic |
| --- | ---: | ---: | ---: |
| Win Rate | 100% | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 | 60.0328 |
| 平均等级 | 1.6667 | 2.0 | 1.0 |
| 平均击杀 | 47.6667 | 48.0 | 46.6667 |
| 平均承伤 | 3.4 | 40.3 | 0.0 |
| 最大执行动作 | 动作 1 = 54.01% | 动作 0 = 31.91% | 动作 0 = 16.01% |
| 归一化动作熵 | 0.4613 | 0.7418 | 0.9803 |
| 平均最高概率动作 | 动作 1 = 0.1909 | 动作 4 = 0.1638 | 动作 0 = 0.1572 |

## 下一步

1. 将该模型作为 observation v2 的 50k PPO 候选基线。
2. 重跑 6 地图 10 seed / 300 秒 deterministic 规则 Bot 对比。
3. 若长局仍低胜率或高承伤，应记录新的 50k v2 failure case，并考虑 100k、300 秒训练 episode、curriculum 或 Boss/hazard reward shaping。
