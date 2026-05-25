# PPO Observation V2 训练基线 001

日期：2026-05-26

## 目标

在 Gym observation v2 增加地图、Boss、hazard 和敌人动态特征后，重新训练 PPO 多地图 random 基线，验证新观察空间是否能避免旧 82 维 observation 在 10k 多地图训练中出现的确定性动作塌缩。

## 训练配置

- Algorithm: `ppo`
- Observation version: `2`
- Observation length: `145`
- Requested timesteps: 10000
- Actual timesteps: 10240
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Entropy coefficient: `0.02`
- Training evaluation policy: `deterministic`
- Paired diagnostic policy: `stochastic`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_rule_bot_comparison`

Observation v2 的 10k PPO 首轮训练已通过确定性动作分布 gate：最大动作为动作 1，占比 54.01%，归一化动作熵为 0.4613。对比旧 observation 的 10k 多地图 random + ent_coef=0.02 实验曾塌缩到单动作 100%，v2 观察空间明显改善了短训阶段的 argmax 可用性。

随机采样诊断同样健康：最大执行动作为动作 1，占比 20.56%，归一化动作熵为 0.9666，平均承伤 0.9。该结果只说明模型可以进入规则 Bot 对比，不代表跨地图 300 秒泛化已经通过。

## 关键指标

| 指标 | Deterministic | Stochastic |
| --- | ---: | ---: |
| Win Rate | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 |
| 平均等级 | 1.6667 | 1.0 |
| 平均击杀 | 47.6667 | 47.0 |
| 平均承伤 | 3.4 | 0.9 |
| 最大执行动作 | 动作 1 = 54.01% | 动作 1 = 20.56% |
| 归一化动作熵 | 0.4613 | 0.9666 |
| 平均最高概率动作 | 动作 1 = 0.1909 | 动作 1 = 0.2101 |

## 判断

- v2 observation 训练链路可用：模型、metadata、training/evaluation/known exploit 报告均已写盘。
- 10k requested timesteps 已足以通过当前动作分布 gate，但仍只是短局 60 秒评估。
- 下一步必须跑 6 地图 10 seed / 300 秒 deterministic 规则 Bot 对比，确认 v2 是否修复旧 100k 模型的跨地图泛化失败。

## 下一步

1. 将该模型作为 observation v2 的首个 PPO 候选基线。
2. 重跑 6 地图 10 seed / 300 秒 deterministic 规则 Bot 对比。
3. 若高压地图仍低胜率或高承伤，记录新的 v2 failure case，再考虑 curriculum、300 秒训练 episode 或 Boss/hazard reward shaping。
