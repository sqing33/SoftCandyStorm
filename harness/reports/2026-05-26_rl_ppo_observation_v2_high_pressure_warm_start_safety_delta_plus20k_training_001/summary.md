# PPO Warm Start Safety Delta 高压训练 +20k 001

日期：2026-05-26

## 目标

从上一轮 high-pressure train300 50k PPO 模型 warm start，切到当前 `safety_delta` reward 后继续训练 20000 requested timesteps，验证能否保留长局模型已有能力，同时改善短局动作 gate。

## 命令要点

- Algorithm：`ppo`
- Warm start model：`python/train/models/ppo_phase1_observation_v2_high_pressure_train300_random_ent002_50000_eval60.zip`
- Requested timesteps：20000
- Actual timesteps：20224
- Training seconds：300
- Training map preset：`high-pressure`
- Training map selection：`random`
- Observation version：2
- Observation len：145
- Algorithm parameters source：`warm_start_metadata`
- Evaluation：5 episode / 60 秒 / deterministic

## 结果

Gate 决策：`trained_needs_rule_bot_comparison`

60 秒 deterministic 评估通过动作分布 gate：

- 胜率：100%
- 平均存活：60.0328 秒
- 平均承伤：7.68
- 平均击杀：48.0
- 平均奖励：4.9846
- 最大动作占比：动作 6 = 48.98%
- 归一化动作熵：0.5640
- 主要动作概率：动作 6 = 0.2239，动作 8 = 0.1533，动作 3 = 0.1395

## Reward Breakdown

- `action_repeat`：-2.128
- `boundary_risk`：-0.3958
- `enemy_pressure`：-0.0188
- `safety_delta`：-0.0027
- `damage_taken`：-0.6144
- `kill`：3.84
- `xp`：1.904
- `terminal`：1.0
- `total`：4.9846

## 结论

Warm start 明显优于从零开始的 `safety_delta` 训练：短局没有动作塌缩，平均承伤也从 31.65 降到 7.68。该模型可以进入 high-pressure 10 seed / 300 秒规则 Bot 对比，但还不能作为平衡或乐趣结论。

## 产物

- Model：`python/train/models/ppo_phase1_observation_v2_high_pressure_warm_start_safety_delta_train300_random_ent002_plus20000_eval60.zip`
- Metadata：`python/train/models/ppo_phase1_observation_v2_high_pressure_warm_start_safety_delta_train300_random_ent002_plus20000_eval60_metadata.json`
- Training report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_warm_start_safety_delta_plus20k_training_001/ppo_training_report.json`
- Evaluation report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_warm_start_safety_delta_plus20k_training_001/ppo_evaluation_report.json`
