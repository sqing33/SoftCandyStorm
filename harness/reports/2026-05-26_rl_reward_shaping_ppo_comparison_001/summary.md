# PPO Reward Shaping 对照实验 001

日期：2026-05-26

## 目标

验证新 Gym reward 不只是让 DQN 摆脱动作塌缩，也能让 PPO 在相同 5000-step / 60 秒烟测窗口内通过动作分布门禁。

## 关键结果

Gate 决策：`trained_needs_rule_bot_comparison` -> `comparison_recorded_not_balance_gate`

| 指标 | PPO 128-step smoke | PPO reward shaping 5000-step |
| --- | --- | --- |
| 实际训练步数 | 256 | 5120 |
| 最大动作占比 | 动作 1 = 100.00% | 动作 5 = 55.47% |
| 归一化动作熵 | 0.0000 | 0.3905 |
| 平均击杀 | 约短局 smoke 水平 | 47.6667 |
| 平均承伤 | 0.0 | 5.5 |
| known exploits | `dominant_action_bias`, `low_action_entropy` | 无 |

规则 Bot 对比中，PPO policy 和 Random/Kite/Tank 都在 3 seed、60 秒窗口内胜利。该结果只说明 PPO policy 已通过动作分布烟测，并且对比链路可用；它仍不是正式平衡门禁。

## Reward Breakdown

```json
{
  "action_repeat": -0.5803,
  "damage_taken": -0.44,
  "kill": 3.8133,
  "level": 0.8,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 6.6333,
  "xp": 1.44
}
```

## 与 DQN 对照

- DQN reward shaping 5000-step：最大动作 35.68%，归一化动作熵 0.6524，平均承伤 33.3。
- PPO reward shaping 5000-step：最大动作 55.47%，归一化动作熵 0.3905，平均承伤 5.5。

两者都通过当前动作塌缩 gate，但策略形态不同。PPO 更集中在动作 5/6，DQN 分布更散但承伤更高；下一步需要更长时长、多地图和更多 seed 才能判断哪种策略更适合作为 RL exploit 压力测试基线。

## 下一步

1. 扩展到至少 10 seed、180 秒以上评估。
2. 覆盖 `frosting-grassland` 之外的地图，优先包含已暴露平衡风险的地图。
3. 继续保持规则 Bot 矩阵为内容门禁主路径，RL policy 只进入辅助压力测试。
