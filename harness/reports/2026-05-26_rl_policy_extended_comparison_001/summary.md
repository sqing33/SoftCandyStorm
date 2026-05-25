# RL Policy 扩样本对比 001

日期：2026-05-26

## 目标

在新 Gym reward 下，不重新训练模型，使用 DQN/PPO reward shaping 5000-step 模型扩展到 10 seed、180 秒，并覆盖训练地图 `frosting-grassland` 与高压验证地图 `caramel-workshop`。

## 结论

Gate 决策：`comparison_recorded_not_balance_gate`

DQN/PPO 在 10 seed、180 秒窗口内均未复发单动作塌缩。所有 policy 的最大动作占比都低于 75%，归一化动作熵都高于 0.25。但该实验仍只记录 RL policy 健康度和泛化迹象，不是内容平衡门禁。

## 结果摘要

| Policy | Map | Win Rate | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DQN | frosting-grassland | 100% | 58.9307 | 259.7 | 动作 2 = 42.36% | 0.5851 |
| PPO | frosting-grassland | 100% | 10.2263 | 256.5 | 动作 5 = 35.91% | 0.4976 |
| DQN | caramel-workshop | 50% | 97.6005 | 143.9 | 动作 2 = 50.77% | 0.4673 |
| PPO | caramel-workshop | 100% | 23.9147 | 258.0 | 动作 2 = 38.56% | 0.4934 |

## 发现

- 新 reward 下 DQN/PPO 的动作分布在更长窗口仍保持健康，说明动作塌缩修复不是 60 秒偶然结果。
- PPO 在两张图上的承伤明显低于 DQN，尤其 `caramel-workshop` 上更稳定。
- DQN 在 `caramel-workshop` 只有 50% 胜率且平均承伤 97.6005，说明单地图训练出的 DQN 泛化不足，后续不应直接把该 DQN 纳入多地图压力测试基线。
- Random/Kite/Tank 在 180 秒窗口中的 gate_status 仍多为 `repair`，说明该窗口不能代替正式 600 秒规则 Bot 平衡矩阵。

## 下一步

1. 优先扩展 PPO 到更多地图、更多 seed 和更长时长，观察是否持续保持低承伤和健康动作分布。
2. DQN 需要多地图训练、更多训练步数或单独的泛化修复，再考虑进入跨地图 RL 压力测试。
3. RL 结果继续只用于 exploit/压力测试辅助，正式内容推进仍依赖规则 Bot 矩阵、Replay 回归和人工试玩。
