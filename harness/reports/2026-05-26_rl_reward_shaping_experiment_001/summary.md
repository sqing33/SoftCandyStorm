# RL Reward Shaping 实验 001

日期：2026-05-26

## 目标

验证调整 Gym reward 后，DQN policy 是否能摆脱单动作塌缩，并进入规则 Bot 对比阶段。

## 改动背景

上一轮 DQN 2000-step / 5000-step 实验显示，单纯增加训练步数只能让策略从动作 5 塌缩转移到动作 4。主要风险是短局 `duration_reached` 终局奖励过高，压过了击杀、拾取、升级和受伤等过程信号。

本轮代码改动只影响 `game_harness gym-bridge` 的 RL reward，不改变 GameCore 规则、Runtime 表现或正式内容数值。

## 关键结果

Gate 决策：`trained_needs_rule_bot_comparison` -> `comparison_recorded_not_balance_gate`

| 指标 | 上一轮 5000-step | 本轮 reward shaping 5000-step |
| --- | --- | --- |
| 最大动作占比 | 动作 4 = 96.91% | 动作 4 = 35.68% |
| 归一化动作熵 | 0.0648 | 0.6524 |
| 平均击杀 | 48.3333 | 48.0 |
| 平均承伤 | 33.8 | 33.3 |
| terminal reward 平均值 | 5.0 | 1.0 |
| known exploits | `dominant_action_bias`, `low_action_entropy` | 无 |

规则 Bot 小样本对比中，policy 和 Random/Kite/Tank 都在 3 seed、60 秒窗口内胜利，因此该报告只证明 RL policy 已通过动作分布烟测，并不证明地图平衡或游戏乐趣。

## Reward Breakdown

本轮 DQN 评估平均奖励：

```json
{
  "action_repeat": -0.4383,
  "damage_taken": -2.664,
  "kill": 3.84,
  "level": 0.5333,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 4.418,
  "xp": 1.5467
}
```

## 风险

- 样本仍只有 3 seed，不能替代正式 Bot 矩阵。
- 60 秒窗口太短，Random/Kite/Tank 全胜说明该窗口不能作为平衡门禁。
- DQN 仍有平均承伤 33.3，需要长窗口和更多地图确认是否学会稳定规避。
- PPO 尚未用新 reward 复测。

## 下一步

1. 用新 reward 跑 PPO 对照，确认不是 DQN 特化结果。
2. 将 DQN/PPO 扩展到更多 seed、更长时长和多地图评估。
3. 保留规则 Bot 作为内容门禁主路径，RL 只作为 exploit 和压力测试补充。
