# PPO 重复动作惩罚随机评估诊断 001

日期：2026-05-26

## 目标

复用增强 `action_repeat` 惩罚后训练出的 PPO 模型，在不重新训练的情况下使用 `--eval-stochastic` 随机采样评估，判断新 reward 下策略分布是否仍有动作熵。

## 评估配置

- Algorithm: `ppo`
- Model: `python/train/models/ppo_phase1_multimap_repeat_penalty_ent002_10000_eval60.zip`
- Map: `frosting-grassland`
- Seed range: `30000-30002`
- Episodes: 3
- Seconds: 60
- Action selection: `stochastic`

## 结论

随机采样评估仍显示健康动作分布：最大动作为动作 6，占比 33.63%，归一化动作熵为 0.8295。与同模型确定性评估的动作 6 占 100%、归一化动作熵 0.0 对比，增强惩罚后的主要问题仍是确定性 argmax 路径塌缩，而不是 PPO 概率分布完全死亡。

该结论不解除 `fail_20260526_009`。正式 RL Bot 基线仍应优先满足确定性、可复现门禁；随机采样评估只作为诊断工具。

## 关键指标

| 指标 | 确定性评估 | 随机采样评估 |
| --- | ---: | ---: |
| Win Rate | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 |
| 平均等级 | 2.0 | 2.0 |
| 平均击杀 | 48.0 | 47.3333 |
| 平均承伤 | 64.55 | 38.9001 |
| 最大动作占比 | 动作 6 = 100.00% | 动作 6 = 33.63% |
| 归一化动作熵 | 0.0 | 0.8295 |

## Reward Breakdown

```json
{
  "action_repeat": 0.0,
  "damage_taken": -3.112,
  "kill": 3.7867,
  "level": 0.8,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 4.6216,
  "xp": 1.5467
}
```

## 判断

- 新 reward 下 stochastic policy 仍保留可用动作熵。
- 确定性策略塌缩不能简单归因于“训练分布完全死掉”。
- 后续应更关注确定性策略质量，例如训练更久、使用 curriculum、调整 PPO 超参，或补充 policy probability / value 诊断，而不是单纯继续加大 `action_repeat` 惩罚。

## 下一步

1. 保留确定性门禁，不用 stochastic 结果替代正式 RL Bot 基线。
2. 下一轮可尝试更长训练步数，并同时输出 deterministic/stochastic 两套评估。
3. 若确定性 argmax 仍塌缩，应考虑记录动作概率分布 top-k，而不是只看采样后的动作计数。
