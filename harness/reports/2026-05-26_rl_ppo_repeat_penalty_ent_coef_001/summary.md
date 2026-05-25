# PPO 重复动作惩罚实验 001

日期：2026-05-26

## 目标

在 `ent_coef=0.02` 仍出现确定性动作塌缩后，增强 Gym bridge 中的 `action_repeat` 惩罚，将同一移动动作的宽限从 45 tick 缩短到 30 tick，并把每 tick 惩罚从 `-0.001` 调整为 `-0.004`。随后使用同样的 6 地图 random PPO 训练配置验证动作分布 gate 是否改善。

## 训练配置

- Algorithm: `ppo`
- Requested timesteps: 10000
- Actual timesteps: 10240
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Entropy coefficient: `0.02`
- Evaluation policy: `deterministic`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_action_bias_repair`

增强 `action_repeat` 惩罚后，固定单方向策略的 reward 已明显变差：本轮评估的 `action_repeat` 平均为 `-6.9907`，平均总 reward 为 `-4.421`。但是 PPO 训练后的确定性策略仍然塌缩到动作 6 占 100.00%，归一化动作熵为 0.0。该模型不得进入规则 Bot 对比、跨地图压力测试或内容门禁判断。

## 关键指标

| 指标 | 结果 |
| --- | ---: |
| Win Rate | 100% |
| 平均存活秒数 | 60.0328 |
| 平均等级 | 2.0 |
| 平均击杀 | 48.0 |
| 平均承伤 | 64.55 |
| 最大动作占比 | 动作 6 = 100.00% |
| 归一化动作熵 | 0.0 |
| `action_repeat` reward | -6.9907 |
| 平均总 reward | -4.421 |
| Gate | `trained_needs_action_bias_repair` |

## Reward Breakdown

```json
{
  "action_repeat": -6.9907,
  "damage_taken": -5.164,
  "kill": 3.84,
  "level": 0.8,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": -4.421,
  "xp": 1.4933
}
```

## 失败原因判断

- Reward shaping 改动已经生效，单方向策略不再是正 reward。
- 10000 requested timesteps 的 PPO 多地图训练仍未学会用确定性策略规避重复动作，说明当前问题不只是惩罚强度不足。
- 可能需要更长训练、curriculum、动作切换/边界特征诊断，或评估 policy probability，才能判断 PPO 是否能在当前离散动作空间中形成可复现策略。

## 下一步

1. 不把该模型推进规则 Bot 对比或跨地图评估。
2. 先记录 stochastic 诊断，确认新 reward 下策略分布是否仍有熵。
3. 下一轮可尝试更长训练步数或更明确的 curriculum，而不是继续只提高惩罚常量。
