# PPO Observation V2 安全风险变化高压地图训练 50k 001

日期：2026-05-26

## 目标

在静态安全塑形过度保守后，改用 `safety_delta` 风险变化奖励重训 high-pressure 地图预设下的 300 秒 PPO，先验证 60 秒短局动作分布是否能通过训练 gate。

## 命令要点

- Algorithm：`ppo`
- Requested timesteps：50000
- Actual timesteps：50176
- Training seconds：300
- Training map preset：`high-pressure`
- Training map selection：`random`
- Observation version：2
- Observation len：145
- `ent_coef`：0.02
- Evaluation：5 episode / 60 秒 / deterministic

## Deterministic 结果

Gate 决策：`trained_needs_action_bias_repair`

60 秒 deterministic 评估没有通过动作分布 gate：

- 胜率：100%
- 平均存活：60.0328 秒
- 平均承伤：31.65
- 平均击杀：48.2
- 平均奖励：-1.0513
- 最大动作占比：动作 6 = 90.74%
- 归一化动作熵：0.1982
- 主要动作概率：动作 6 = 0.2515，动作 0 = 0.1505，动作 1 = 0.1345

## Stochastic 诊断

同一模型用 `--eval-stochastic` 复查 5 episode / 60 秒：

- 胜率：100%
- 平均存活：60.0328 秒
- 平均承伤：11.94
- 平均奖励：6.151
- 最大动作占比：动作 6 = 25.57%
- 归一化动作熵：0.9007

这说明 policy 概率分布仍保留可用动作质量，但 deterministic argmax 会严重偏向动作 6；当前默认训练 gate 仍应判定为 repair，不能进入 deterministic 300 秒规则 Bot 对比。

## Reward Breakdown

Deterministic 评估中的关键平均字段：

- `action_repeat`：-5.6016
- `boundary_risk`：-0.6063
- `enemy_pressure`：-0.0521
- `safety_delta`：-0.0036
- `damage_taken`：-2.532
- `kill`：3.856
- `xp`：1.488
- `terminal`：1.0
- `total`：-1.0514

## 结论

`safety_delta` 没有复现上一轮静态 safety reward 的短局低承伤优势，也让 deterministic policy 回到动作塌缩。由于训练 gate 已失败，本轮不推进 high-pressure 10 seed / 300 秒 deterministic 对比。下一步应先决定 RL 测试 Bot 是否允许 seeded stochastic policy；如果仍要求 deterministic policy，则需要继续修训练目标或评估策略，而不是直接拉长训练。

## Failure Case

- `harness/failed_cases/fail_20260526_016_ppo_safety_delta_action_collapse.json`

## 产物

- Model：`python/train/models/ppo_phase1_observation_v2_high_pressure_safety_delta_train300_random_ent002_50000_eval60.zip`
- Metadata：`python/train/models/ppo_phase1_observation_v2_high_pressure_safety_delta_train300_random_ent002_50000_eval60_metadata.json`
- Training report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_safety_delta_train300_50k_training_001/ppo_training_report.json`
- Evaluation report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_safety_delta_train300_50k_training_001/ppo_evaluation_report.json`
- Stochastic diagnostic：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_safety_delta_train300_50k_training_001/ppo_stochastic_evaluation_report.json`
