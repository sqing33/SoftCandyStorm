# PPO 多地图 entropy 实验 001

日期：2026-05-26

## 目标

在 `cycle` 和 `random` 多地图训练均出现单动作塌缩后，使用新增的 `--ent-coef` 覆盖入口提高 PPO entropy 系数，验证 `ent_coef=0.02` 是否能修复 6 张 `base_demo` 地图训练后的动作分布 gate。

## 训练配置

- Algorithm: `ppo`
- Requested timesteps: 10000
- Actual timesteps: 10240
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Entropy coefficient: `0.02`
- Evaluation: 3 seed / 60 秒默认确定性评估

## 结论

Gate 决策：`trained_needs_action_bias_repair`

`ent_coef=0.02` 未能修复多地图 PPO 的动作塌缩。训练后确定性评估中动作 5 占 100.00%，归一化动作熵为 0.0。该模型不得进入规则 Bot 对比、跨地图压力测试或内容门禁判断。

## 关键指标

| 指标 | 结果 |
| --- | ---: |
| Win Rate | 100% |
| 平均存活秒数 | 60.0328 |
| 平均等级 | 1.0 |
| 平均击杀 | 47.0 |
| 平均承伤 | 5.45 |
| 最大动作占比 | 动作 5 = 100.00% |
| 归一化动作熵 | 0.0 |
| Gate | `trained_needs_action_bias_repair` |

## Algorithm Parameters

```json
{
  "learning_rate": 0.0003,
  "n_steps": 256,
  "batch_size": 64,
  "gamma": 0.99,
  "gae_lambda": 0.95,
  "ent_coef": 0.02,
  "clip_range": 0.2
}
```

## Reward Breakdown

```json
{
  "action_repeat": -1.756,
  "damage_taken": -0.436,
  "kill": 3.76,
  "level": 0.0,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 3.6483,
  "xp": 0.48
}
```

## 失败原因判断

- `--ent-coef` 覆盖入口已生效，并且训练报告正确记录了最终 SB3 参数。
- `0.02` entropy 系数不足以让当前多地图 PPO 在确定性评估中摆脱单动作 argmax。
- 60 秒短评估仍能让单方向策略获胜，说明 reward 和动作惩罚仍不足以要求策略主动规避、拾取或切换方向。

## 下一步

1. 不再把 `ent_coef=0.02` 模型推进到规则 Bot 对比。
2. 下一轮可尝试更高 entropy 系数，例如 `0.05` 或 `0.1`，但应同时考虑增强 `action_repeat` / 边界停留惩罚。
3. 可补充非确定性评估或 policy probability 诊断，用来区分“训练分布仍有熵”与“确定性部署动作塌缩”。
