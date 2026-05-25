# PPO Soda Focus Warm Start 高压地图对比 +20k 001

日期：2026-05-26

## 目标

验证只在 `soda-creek` 继续训练的 warm-start safety_delta 模型，是否能改善 `soda-creek` 300 秒长局，同时不破坏其他 high-pressure 地图。

## 命令要点

- Algorithm：`ppo`
- Model：`python/train/models/ppo_phase1_observation_v2_soda_focus_warm_start_safety_delta_train300_ent002_plus20000_eval_soda60.zip`
- Action selection：`deterministic`
- Compare map preset：`high-pressure`
- Maps：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- Seeds：30000-30009
- Evaluation seconds：300
- Rule Bots：`random`、`kite`、`tank`

## 聚合结果

Gate 决策：`multimap_comparison_recorded_needs_policy_repair`

| Map | Policy 胜率 | 平均存活 | 平均承伤 | 最大动作 | 归一化动作熵 | 最佳规则 Bot 胜率 |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| `soda-creek` | 0% | 146.6294s | 120.2034 | 动作 8 = 28.29% | 0.8035 | 50% |
| `caramel-workshop` | 0% | 212.7098s | 120.5527 | 动作 8 = 37.98% | 0.7764 | 40% |
| `cracked-star-jar` | 10% | 206.6464s | 119.0446 | 动作 8 = 29.03% | 0.8061 | 50% |

总体：

- 平均胜率：3.33%
- 最低胜率：0%
- 平均存活：188.6619 秒
- repair maps：`soda-creek`、`caramel-workshop`

## 结论

Soda-focused 训练提升了动作熵，但没有提升目标地图胜率，反而让 `soda-creek` 和 `caramel-workshop` 回到 0%。这说明单图继续训练会改变移动偏好并削弱原本的 high-pressure 泛化，不能作为下一步主线。应回到多图 curriculum 或规则 Bot 轨迹蒸馏，而不是继续单图 PPO 微调。

## Failure Case

- `harness/failed_cases/fail_20260526_018_soda_focus_warm_start_regression.json`

## 产物

- Comparison report：`harness/reports/2026-05-26_rl_ppo_observation_v2_soda_focus_warm_start_safety_delta_plus20k_comparison_001/high_pressure_comparison.json`
