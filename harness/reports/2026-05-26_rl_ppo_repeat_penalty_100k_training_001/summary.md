# PPO 重复动作惩罚 100k 训练实验 001

日期：2026-05-26

## 目标

在 50000-step PPO 已接近动作分布门禁但最大动作占比仍为 80.23% 后，本轮将训练规模提高到 100000 requested timesteps，继续使用 6 地图 random 训练、`ent_coef=0.02` 和增强后的 `action_repeat` 惩罚，验证确定性 argmax 策略是否能通过动作分布 gate。

## 训练配置

- Algorithm: `ppo`
- Requested timesteps: 100000
- Actual timesteps: 100096
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Entropy coefficient: `0.02`
- Training evaluation policy: `deterministic`
- Paired diagnostic policy: `stochastic`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_rule_bot_comparison`

100000-step 训练首次通过确定性动作分布 gate：最大动作为动作 7，占比 52.93%，归一化动作熵为 0.4491。与 50000-step 的动作 3 占 80.23%、归一化动作熵 0.2876 相比，确定性 argmax 已经从“接近门禁”推进到“允许进入规则 Bot 对比”。

随机采样诊断同样健康：最大动作为动作 7，占比 31.67%，归一化动作熵为 0.8896，说明概率策略仍保持较高探索分布。该结果不能替代确定性门禁，但能支持继续做跨地图对比。

## 关键指标

| 指标 | 50000-step 确定性 | 100000-step 确定性 | 100000-step 随机采样 |
| --- | ---: | ---: | ---: |
| Win Rate | 100% | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 | 60.0328 |
| 平均等级 | 1.0 | 2.0 | 1.6667 |
| 平均击杀 | 46.6667 | 47.3333 | 47.6667 |
| 平均承伤 | 4.6 | 22.85 | 16.9 |
| 最大动作占比 | 动作 3 = 80.23% | 动作 7 = 52.93% | 动作 7 = 31.67% |
| 归一化动作熵 | 0.2876 | 0.4491 | 0.8896 |
| `action_repeat` reward | -4.6693 | -1.068 | 0.0 |
| 平均总 reward | 0.8563 | 5.131 | 6.0883 |

## Deterministic Reward Breakdown

```json
{
  "action_repeat": -1.068,
  "damage_taken": -1.828,
  "kill": 3.7867,
  "level": 0.8,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 5.131,
  "xp": 1.84
}
```

## Stochastic Reward Breakdown

```json
{
  "action_repeat": 0.0,
  "damage_taken": -1.352,
  "kill": 3.8133,
  "level": 0.5333,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 6.0883,
  "xp": 1.4933
}
```

## 判断

- 100000-step PPO 模型已经通过当前 RL 动作分布门禁：最大动作占比低于 75%，归一化动作熵高于 0.25。
- 该结论只表示模型可进入规则 Bot 对比，不表示可作为正式内容、平衡或乐趣门禁。
- 确定性评估承伤高于 50000-step，但动作分布明显更健康；下一步必须用多地图长局对比判断泛化质量。

## 下一步

1. 保留该模型作为当前 PPO 多地图训练候选基线。
2. 运行 deterministic 6 地图 10 seed / 300 秒规则 Bot 对比，并重点观察 `soda-creek`、`caramel-workshop`、`cracked-star-jar` 是否仍有泛化掉线。
3. 若跨地图对比暴露胜率、承伤或击杀不足，应记录新的 failure case；若通过，也仍只能作为 RL 测试 Bot 候选，不能替代规则 Bot 和人工试玩。
