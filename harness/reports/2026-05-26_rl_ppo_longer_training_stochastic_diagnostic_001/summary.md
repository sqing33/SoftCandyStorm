# PPO 长训练随机评估诊断 001

日期：2026-05-26

## 目标

复用 50000-step PPO 长训练模型，使用 `--eval-stochastic` 随机采样评估，补齐 deterministic/stochastic 成对诊断，判断该模型的概率策略是否已经明显优于确定性 argmax 结果。

## 评估配置

- Algorithm: `ppo`
- Model: `python/train/models/ppo_phase1_multimap_repeat_penalty_ent002_50000_eval60.zip`
- Map: `frosting-grassland`
- Seed range: `30000-30002`
- Episodes: 3
- Seconds: 60
- Action selection: `stochastic`

## 结论

随机采样评估表现健康：最大动作为动作 3，占比 27.60%，归一化动作熵为 0.8648，平均承伤为 2.05。与同模型确定性评估的动作 3 占 80.23%、归一化动作熵 0.2876 对比，50000-step 模型的概率策略已经比较分散，但确定性 argmax 仍未过最大动作占比门禁。

该结论不解除 `fail_20260526_010`。正式 RL Bot 基线仍以确定性可复现策略为准；随机采样评估用于诊断训练是否有进一步推进价值。

## 关键指标

| 指标 | 确定性评估 | 随机采样评估 |
| --- | ---: | ---: |
| Win Rate | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 |
| 平均等级 | 1.0 | 1.0 |
| 平均击杀 | 46.6667 | 47.0 |
| 平均承伤 | 4.6 | 2.05 |
| 最大动作占比 | 动作 3 = 80.23% | 动作 3 = 27.60% |
| 归一化动作熵 | 0.2876 | 0.8648 |

## Reward Breakdown

```json
{
  "action_repeat": 0.0,
  "damage_taken": -0.164,
  "kill": 3.76,
  "level": 0.0,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 5.8096,
  "xp": 0.6133
}
```

## 判断

- 更长训练后的 stochastic policy 已明显健康。
- 确定性 argmax 仍偏向动作 3，但已经从完全塌缩转为接近门禁。
- 继续训练或 curriculum 有希望让确定性 gate 过线，但不能用 stochastic 结果替代确定性门禁。

## 下一步

1. 可尝试 100000-step 训练，优先观察确定性最大动作占比是否低于 75%。
2. 若 100000-step 仍未过线，应补 policy probability top-k 诊断，而不是只看采样动作计数。
3. 通过确定性动作 gate 后，再做 6 地图 10 seed / 300 秒对比。
