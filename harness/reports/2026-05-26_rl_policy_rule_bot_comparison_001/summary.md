# DQN Policy 与规则 Bot 对比报告

- 算法：`dqn`
- 模型：`python/train/models/dqn_phase1_movement_survival.zip`
- 地图：`frosting-grassland`
- Seeds：`30000`..`30001`
- 单局时长：`5` 秒
- 规则 Bot：`random`、`kite`、`tank`
- 报告：`harness/reports/2026-05-26_rl_policy_rule_bot_comparison_001/dqn_rule_bot_comparison.json`
- Failure case：`harness/failed_cases/fail_20260526_003_dqn_dominant_action_bias.json`

## 执行命令

```bash
uv run --with 'gymnasium>=1.0,<2' --with 'numpy>=1.26' --with 'stable-baselines3>=2.0,<3' python python/train/train_sb3.py --algorithm dqn --compare-rule-bots --model python/train/models/dqn_phase1_movement_survival.zip --seed-start 30000 --eval-episodes 2 --eval-seconds 5 --map-id frosting-grassland --rule-bots random,kite,tank --report harness/reports/2026-05-26_rl_policy_rule_bot_comparison_001/dqn_rule_bot_comparison.json
```

## 结果

| Policy / Bot | Win Rate | Avg Survival | Avg Level | Avg Kills | Avg Damage Taken |
|---|---:|---:|---:|---:|---:|
| DQN policy | 100% | 5.0333 | 1.0 | 1.5 | 0.0 |
| RandomBot | 100% | 5.033 | 1.0 | 3.0 | 0.0 |
| KiteBot | 100% | 5.033 | 1.0 | 3.0 | 0.0 |
| TankBot | 100% | 5.033 | 1.0 | 3.0 | 0.0 |

## 发现

- DQN policy 在 302 个 step 中 `100%` 选择动作 `1`，触发 `dominant_action_bias`。
- 这次对比只有 2 个 seed、5 秒时长，只能证明报告链路和同 seed / 同 map 对比能力可用。
- 规则 Bot 在 5 秒窗口内全部胜利，矩阵 gate 显示 `repair` 是因为该窗口远短于正式平衡评估窗口，不能按 600 秒胜率目标解读。
- Gate 结论：`comparison_recorded_not_balance_gate`。

## 后续

- 修复或约束 DQN 训练的动作塌缩问题，至少记录动作熵、动作分布和奖励拆解。
- 再进行更长时长、更多 seed 的 RL policy 对比。
- PPO 冒烟仍可作为第二条 SB3 算法链路验证，但不能替代 DQN 动作偏置修复。
