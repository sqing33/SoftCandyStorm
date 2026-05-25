# PPO 100k 多地图规则 Bot 对比 001

日期：2026-05-26

## 目标

复用已经通过确定性动作分布 gate 的 100000-step PPO 多地图 random 训练模型，在全部 6 张 `base_demo` 地图上运行 10 seed、300 秒 deterministic 评估，并与 Random/Kite/Tank 规则 Bot 做同 seed 对比，确认跨地图泛化是否修复。

## 结论

Gate 决策：`repair`

100k PPO policy 没有复发动作塌缩：6 张地图最大动作占比均低于 75%，归一化动作熵均高于 0.25。但跨地图泛化仍失败，且比 5000-step 对照在高压地图上更差：`soda-creek` 胜率 10%，`caramel-workshop` 和 `cracked-star-jar` 胜率均为 0%，平均承伤均接近或超过 120。该 policy 不能作为正式跨地图 RL 压力测试基线。

`compare-rule-bots` 报告自身的 `gate_decision` 只检查 action bias；本 summary 的 `repair` 是基于跨地图胜率、承伤和规则 Bot 参考做出的 Harness 结论。

## 结果摘要

| Map | PPO Win Rate | 平均存活秒数 | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 | 规则 Bot 参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| frosting-grassland | 90% | 291.1851 | 78.4534 | 505.8 | 动作 7 = 71.57% | 0.3127 | Random 70%，Kite 90%，Tank 100% |
| soda-creek | 10% | 107.9392 | 119.7071 | 207.6 | 动作 7 = 51.94% | 0.5979 | Random 0%，Kite 10%，Tank 50% |
| cotton-cloud-pasture | 100% | 300.015 | 64.6721 | 554.8 | 动作 7 = 72.34% | 0.3160 | Random 20%，Kite/Tank 100% |
| caramel-workshop | 0% | 215.5938 | 120.5158 | 333.5 | 动作 7 = 67.98% | 0.4041 | Random 0%，Kite 40%，Tank 20% |
| jelly-platform | 70% | 273.8554 | 94.5454 | 604.3 | 动作 7 = 68.80% | 0.4442 | Random 0%，Kite/Tank 100% |
| cracked-star-jar | 0% | 199.7522 | 120.4954 | 429.5 | 动作 7 = 62.17% | 0.5105 | Random 0%，Kite 40%，Tank 50% |

## 通过项

- 动作分布 gate 通过：所有地图最大动作占比低于 75%。
- 动作熵 gate 通过：所有地图归一化动作熵高于 0.25。
- 报告链路完整：每张地图都包含 policy summary、reward_breakdown、rule_bot_matrix、findings 和 rule_bot_command。

## 失败项

- 跨地图泛化不足：3 张地图低于 50% 胜率，其中 2 张地图为 0%。
- 承伤偏高：`soda-creek`、`caramel-workshop`、`cracked-star-jar` 平均承伤约 120，`jelly-platform` 也接近 95。
- 策略形态偏单一：虽然未超过 75% gate，但 6 张地图的最大动作都集中在动作 7，`cotton-cloud-pasture` 和 `frosting-grassland` 已接近上限。
- 规则 Bot 参考本身也提示地图/seed 组合压力不均，尤其部分 high-skill Bot 未进目标区间；本轮不能作为内容平衡结论，只能作为 RL policy 泛化失败记录。

## Failure Case

- `harness/failed_cases/fail_20260526_011_ppo_100k_multimap_generalization_gap.json`

## 下一步

1. 不把该 100k PPO policy 推进为正式 RL 压力测试 Bot。
2. 优先做训练诊断：记录 policy probability top-k、检查地图条件是否足以被策略利用，并分析动作 7 在不同地图上的空间含义。
3. 后续修复可尝试 curriculum、按地图分阶段训练、延长 300 秒训练 episode 或加入中后期/Boss/hazard reward shaping。
4. 修复后必须重跑同一 6 地图 10 seed / 300 秒 deterministic 对比；通过后再扩到 600 秒和更多 seed。
