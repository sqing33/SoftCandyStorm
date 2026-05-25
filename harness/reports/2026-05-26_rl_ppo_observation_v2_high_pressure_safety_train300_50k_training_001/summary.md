# PPO Observation V2 安全塑形高压地图训练 50k 001

日期：2026-05-26

## 目标

在 Gym reward 增加 `low_health`、`boundary_risk`、`enemy_pressure`、`hazard_risk`、`boss_pressure` 安全塑形字段后，复用 high-pressure 地图预设和 300 秒训练 episode 重训 50k PPO，验证短局动作分布和承伤是否保持健康。

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

## 结果

Gate 决策：`trained_needs_rule_bot_comparison`

60 秒 deterministic 评估通过动作分布 gate：

- 胜率：100%
- 平均存活：60.0328 秒
- 平均承伤：1.8
- 平均击杀：46.8
- 最大动作占比：动作 4 = 46.40%
- 归一化动作熵：0.5048
- 主要动作概率：动作 4 = 0.2066，动作 8 = 0.1851，动作 5 = 0.1359

## Reward Breakdown

安全塑形字段已进入评估报告：

- `boundary_risk`：-0.3824
- `enemy_pressure`：-0.0259
- `low_health`：0.0
- `hazard_risk`：0.0
- `boss_pressure`：0.0
- `damage_taken`：-0.144
- `action_repeat`：-4.0032

## 结论

与上一轮 high-pressure train300 50k 模型相比，短局承伤从 36.21 降到 1.8，最大动作占比从动作 8 的 54.50% 降到动作 4 的 46.40%，动作熵从 0.4614 升到 0.5048。安全塑形没有造成短局动作塌缩，可以进入 high-pressure 10 seed / 300 秒聚合对比。

## 产物

- Model：`python/train/models/ppo_phase1_observation_v2_high_pressure_safety_train300_random_ent002_50000_eval60.zip`
- Metadata：`python/train/models/ppo_phase1_observation_v2_high_pressure_safety_train300_random_ent002_50000_eval60_metadata.json`
- Training report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_safety_train300_50k_training_001/ppo_training_report.json`
- Evaluation report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_safety_train300_50k_training_001/ppo_evaluation_report.json`
