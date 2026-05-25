# DQN 动作塌缩修复实验 001

日期：2026-05-26

## 目标

验证“扩大 DQN 训练步数与评估窗口”是否足以修复最小训练冒烟中出现的单动作塌缩。

## 输入与产物

- 128-step 默认 DQN smoke 复现：`harness/reports/2026-05-26_rl_dqn_training_smoke_001/dqn_training_smoke.json`
- 2000-step / 30 秒评估：`dqn_training_2000_eval30.json`
- 5000-step / 60 秒评估：`dqn_training_5000_eval60.json`
- 5000-step 独立模型：`python/train/models/dqn_phase1_movement_survival_5000_eval60.zip`
- 5000-step 规则 Bot 对比：`dqn_rule_bot_comparison_5000_eval60.json`

## 结论

Gate 决策：`repair`

这轮实验没有修复 DQN 动作塌缩。单纯把训练从 128 steps 扩大到 2000 或 5000 steps，会改变塌缩到哪个动作，但不会形成稳定、可解释的移动策略。

## 关键结果

| 实验 | 评估窗口 | Gate | 最大动作占比 | 动作熵 | 备注 |
| --- | --- | --- | --- | --- | --- |
| DQN 128-step smoke 复现 | 2 episodes x 5 秒 | `trained_needs_action_bias_repair` | 动作 5 = 100.00% | 0.0000 | 冒烟链路可用，但策略不可用 |
| DQN 2000-step | 3 episodes x 30 秒 | `trained_needs_action_bias_repair` | 动作 5 = 81.72% | 0.3735 | 高于 75% 阈值，且终局奖励占主导 |
| DQN 5000-step | 3 episodes x 60 秒 | `trained_needs_action_bias_repair` | 动作 4 = 96.91% | 0.0648 | 塌缩动作从 5 转移到 4，平均承伤 33.8 |

规则 Bot 同 map / 同 seed 小样本对比中，Random、Kite、Tank 均为 3/3 胜利，因此报告只记录链路结果，不作为平衡通过依据。该现象反而提示 `frosting-grassland` 60 秒窗口过短或压力过低，不能用来证明 RL 策略质量。

## 风险

- 当前 DQN 奖励仍容易被短局 `duration_reached` 终局奖励带偏。
- 扩大训练步数会复现或转移动作塌缩，而不是自然解决它。
- 规则 Bot 对比样本只有 3 seed，低于正式 Bot 矩阵要求。
- RL Bot 结果不能替代人工可玩性结论。

## 下一步

1. 调整 reward shaping，降低短局终局奖励的支配性，并提高拾取、威胁规避、空间控制的可学习信号。
2. 增加动作塌缩惩罚或动作变化观察字段，避免策略长期停在单一方向。
3. 用更长 episode 和更多 seed 重新运行 DQN/PPO 对照。
4. 只有当最大动作占比低于 75%、归一化动作熵高于 0.25 后，才进入同 seed / 同 map 规则 Bot 对比。
