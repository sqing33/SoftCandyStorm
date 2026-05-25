# PPO Safety Delta 高压地图 Stochastic 对比 001

日期：2026-05-26

## 目标

上一轮 `safety_delta` PPO 模型在 60 秒 deterministic 评估中出现动作 6 占 90.74% 的 argmax 塌缩，但 stochastic 诊断动作熵健康。本轮用同一模型跑 seeded stochastic high-pressure 3 地图、10 seed、300 秒聚合对比，判断它是否只是 deterministic 选择策略失败。

## 命令要点

- Algorithm：`ppo`
- Model：`python/train/models/ppo_phase1_observation_v2_high_pressure_safety_delta_train300_random_ent002_50000_eval60.zip`
- Action selection：`stochastic`
- Compare map preset：`high-pressure`
- Maps：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- Seeds：30000-30009
- Evaluation seconds：300
- Rule Bots：`random`、`kite`、`tank`

## 聚合结果

Gate 决策：`multimap_comparison_recorded_needs_policy_repair`

| Map | Policy 胜率 | 平均存活 | 平均承伤 | 最大动作 | 归一化动作熵 | 最佳规则 Bot 胜率 |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| `soda-creek` | 0% | 70.0718s | 120.3494 | 动作 6 = 22.25% | 0.9273 | 50% |
| `caramel-workshop` | 0% | 188.7368s | 120.5089 | 动作 6 = 23.40% | 0.9201 | 40% |
| `cracked-star-jar` | 0% | 156.9941s | 120.4155 | 动作 6 = 22.00% | 0.9267 | 50% |

总体：

- 平均胜率：0%
- 平均存活：138.6009 秒
- repair maps：`soda-creek`、`caramel-workshop`、`cracked-star-jar`

## 结论

Seeded stochastic 选择解决了动作分布问题，但没有解决高压长局生存问题。相比静态 safety reward，平均存活略有改善；相比无 safety_delta 的 high-pressure train300 50k 模型，三张图仍明显退化。因此当前问题不是单纯 deterministic argmax，而是 reward/observation/training curriculum 仍不足以学到高压地图的危险规避与续航。

## Failure Case

- `harness/failed_cases/fail_20260526_017_ppo_safety_delta_stochastic_gap.json`

## 产物

- Comparison report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_safety_delta_train300_50k_stochastic_comparison_001/high_pressure_stochastic_comparison.json`
