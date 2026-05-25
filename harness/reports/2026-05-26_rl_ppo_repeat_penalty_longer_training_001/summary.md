# PPO 重复动作惩罚长训练实验 001

日期：2026-05-26

## 目标

在增强 `action_repeat` 惩罚后，10000-step PPO 仍出现确定性动作塌缩。本轮将训练规模提高到 50000 requested timesteps，保持 6 地图 random 训练与 `ent_coef=0.02`，验证更长训练是否能通过确定性动作分布 gate。

## 训练配置

- Algorithm: `ppo`
- Requested timesteps: 50000
- Actual timesteps: 50176
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Entropy coefficient: `0.02`
- Evaluation policy: `deterministic`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_action_bias_repair`

50000-step 训练明显改善了确定性动作分布，但仍未通过 gate：最大动作从 100.00% 降到动作 3 占 80.23%，归一化动作熵从 0.0 提升到 0.2876。当前动作熵已高于 0.25 阈值，但最大动作占比仍高于 75%，所以模型仍不得进入规则 Bot 对比、跨地图压力测试或内容门禁判断。

## 关键指标

| 指标 | 10000-step | 50000-step |
| --- | ---: | ---: |
| Win Rate | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 |
| 平均等级 | 2.0 | 1.0 |
| 平均击杀 | 48.0 | 46.6667 |
| 平均承伤 | 64.55 | 4.6 |
| 最大动作占比 | 动作 6 = 100.00% | 动作 3 = 80.23% |
| 归一化动作熵 | 0.0 | 0.2876 |
| `action_repeat` reward | -6.9907 | -4.6693 |
| 平均总 reward | -4.421 | 0.8563 |

## Reward Breakdown

```json
{
  "action_repeat": -4.6693,
  "damage_taken": -0.368,
  "kill": 3.7333,
  "level": 0.0,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 0.8563,
  "xp": 0.56
}
```

## 失败原因判断

- 更长训练确实缓解了确定性 argmax 塌缩，动作熵已达标。
- 最大动作占比仍超出 75% gate，说明当前 PPO 仍偏向单方向主策略。
- 承伤显著降低，说明策略质量可能有所提升，但不能因为生存指标好看就跳过动作分布门禁。

## 下一步

1. 不把该模型推进规则 Bot 对比或跨地图压力测试。
2. 可以继续尝试 100000-step 训练，或先加入 curriculum / policy probability 诊断。
3. 下一轮仍必须同时记录 deterministic 与 stochastic 两套动作分布；确定性 gate 通过后才允许跑 6 地图 10 seed / 300 秒对比。
