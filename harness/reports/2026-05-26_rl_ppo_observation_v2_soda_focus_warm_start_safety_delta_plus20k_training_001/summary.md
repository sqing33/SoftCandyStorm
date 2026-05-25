# PPO Soda Focus Warm Start Safety Delta +20k 训练 001

日期：2026-05-26

## 目标

上一轮 warm-start + `safety_delta` 在 high-pressure 聚合中表现出正向信号，但 `soda-creek` 平均存活低于 fail_014。本轮只在 `soda-creek` 上继续训练 20000 requested timesteps，并使用 `--map-id soda-creek` 做训练后短局评估，验证定向训练是否能改善该地图。

## 命令要点

- Algorithm：`ppo`
- Warm start model：`python/train/models/ppo_phase1_observation_v2_high_pressure_warm_start_safety_delta_train300_random_ent002_plus20000_eval60.zip`
- Requested timesteps：20000
- Actual timesteps：20224
- Training maps：`soda-creek`
- Training seconds：300
- Evaluation map：`soda-creek`
- Evaluation：5 episode / 60 秒 / deterministic
- Algorithm parameters source：`warm_start_metadata`

## 结果

Gate 决策：`trained_needs_rule_bot_comparison`

`soda-creek` 60 秒 deterministic 评估：

- 胜率：40%
- 平均存活：57.3328 秒
- 平均承伤：85.966
- 平均击杀：64.2
- 最大动作占比：动作 6 = 28.28%
- 归一化动作熵：0.7681
- 主要动作概率：动作 8 = 0.1835，动作 6 = 0.1741，动作 0 = 0.1556

## Reward Breakdown

- `action_repeat`：-1.0248
- `boundary_risk`：-0.4382
- `enemy_pressure`：-0.1408
- `safety_delta`：-0.0089
- `damage_taken`：-6.8773
- `kill`：5.136
- `terminal`：-1.4
- `total`：-0.3245

## 结论

该模型没有动作塌缩，动作熵显著高于上一轮 high-pressure warm-start；但短局 `soda-creek` 胜率只有 40%，说明该地图压力已在 60 秒内暴露。按当前训练 gate 可进入 300 秒高压对比，但需要重点观察是否牺牲其他地图泛化。

## 产物

- Model：`python/train/models/ppo_phase1_observation_v2_soda_focus_warm_start_safety_delta_train300_ent002_plus20000_eval_soda60.zip`
- Metadata：`python/train/models/ppo_phase1_observation_v2_soda_focus_warm_start_safety_delta_train300_ent002_plus20000_eval_soda60_metadata.json`
- Training report：`harness/reports/2026-05-26_rl_ppo_observation_v2_soda_focus_warm_start_safety_delta_plus20k_training_001/ppo_training_report.json`
- Evaluation report：`harness/reports/2026-05-26_rl_ppo_observation_v2_soda_focus_warm_start_safety_delta_plus20k_training_001/ppo_evaluation_report.json`
