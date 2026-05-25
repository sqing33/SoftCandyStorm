# PPO Observation V2 高压地图 300 秒训练 50k 001

日期：2026-05-26

## 目标

使用 observation v2、`high-pressure` 地图预设和 300 秒训练 episode，重训 PPO 多地图策略，验证把训练窗口对齐到长局高压地图后，短局动作分布是否仍保持健康。

训练地图：

- `soda-creek`
- `caramel-workshop`
- `cracked-star-jar`

## 命令要点

- Algorithm：`ppo`
- Requested timesteps：50000
- Actual timesteps：50176
- Training seconds：300
- Training map selection：`random`
- Training map preset：`high-pressure`
- Observation version：2
- Observation len：145
- `ent_coef`：0.02
- Evaluation：5 episode / 60 秒 / deterministic

## 结果

Gate 决策：`trained_needs_rule_bot_comparison`

60 秒 deterministic 评估通过动作分布 gate：

- 胜率：100%
- 平均存活：60.0328 秒
- 平均承伤：36.21
- 平均击杀：48.2
- 最大动作占比：动作 8 = 54.50%
- 归一化动作熵：0.4614
- 主要动作概率：动作 8 = 0.2843，动作 6 = 0.2368，动作 5 = 0.1551

## 结论

300 秒训练 episode 没有导致短局 deterministic 动作塌缩；该模型可以进入高压地图 300 秒规则 Bot 对比。但 60 秒默认评估不能证明跨地图泛化已经修复，必须继续跑 `high-pressure` 的 10 seed / 300 秒对比。

## 产物

- Model：`python/train/models/ppo_phase1_observation_v2_high_pressure_train300_random_ent002_50000_eval60.zip`
- Metadata：`python/train/models/ppo_phase1_observation_v2_high_pressure_train300_random_ent002_50000_eval60_metadata.json`
- Training report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_train300_50k_training_001/ppo_training_report.json`
- Evaluation report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_train300_50k_training_001/ppo_evaluation_report.json`
