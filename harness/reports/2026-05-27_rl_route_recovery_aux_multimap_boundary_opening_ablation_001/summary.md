# Route Recovery Aux Multimap Boundary Opening Ablation

## 结论

- Gate decision: `ablation_recorded_not_policy_gate`
- Source samples: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_samples_001/multimap_boundary_samples.jsonl`
- Baseline regression: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_001/summary.md`
- Variants: `no_class_weight_1_0`、`no_class_weight_1_5`、`no_class_weight_2_0`

本轮只做参数消融，不推进 stage 03。目标是确认上一轮 action `6` dominant bias 是否主要来自 `inverse_frequency` class weighting，以及降低 `edge_recovery_sample_weight` 是否能改善 60 秒 high-pressure 三图表现。

## Variant Results

| Variant | Class weighting | Edge weight | Gate | soda win | soda dominant | caramel dominant | cracked win | cracked dominant |
| --- | --- | ---: | --- | ---: | --- | --- | ---: | --- |
| `no_class_weight_1_0` | `none` | `1.0` | `multimap_comparison_recorded_watch` | `0.4` | action `6` `0.4950` | action `6` `0.4282` | `0.4` | action `6` `0.3798` |
| `no_class_weight_1_5` | `none` | `1.5` | `multimap_comparison_recorded_not_balance_gate` | `0.4` | action `6` `0.5289` | action `6` `0.6803` | `0.8` | action `6` `0.5650` |
| `no_class_weight_2_0` | `none` | `2.0` | `multimap_comparison_recorded_not_balance_gate` | `0.4` | action `6` `0.4355` | action `6` `0.6985` | `0.8` | action `6` `0.3797` |

## 判断

移除 `inverse_frequency` 后，action `6` 在 `soda-creek` 和 `cracked-star-jar` 的 dominant ratio 明显低于上一轮 `0.77 / 0.72`，说明 class weighting 是 action `6` 过补偿的重要来源。但三种权重都没有让 `soda-creek` 超过 `0.4` win_rate，且 `caramel-workshop` 在 `weight=1.5/2.0` 仍接近 action-bias 阈值。

当前最可参考的消融是 `no_class_weight_2_0`：它在 `soda-creek` 的 damage_taken 从上一轮 `106.7094` 降到 `86.6326`，在 `cracked-star-jar` win_rate 达到 `0.8`，但仍不是可推进策略。该结果只能说明“去掉 class weighting 值得保留”，不能证明 route recovery 已修复。

## 下一步

- 保留 `class_weighting = none` 作为后续 opening repair 默认候选
- 不继续单纯调大 edge recovery 权重
- 下一轮应诊断 online-prefix 历史和 action `6` 偏置来源，或改为 teacher soft target / 多动作分布目标
- 任意新 checkpoint 仍必须先过 60 秒 high-pressure 三图 deterministic gate，再考虑 180 / 300 秒长窗

## 输出文件

每个 variant 目录包含：

- `opening_training.json`
- `packaging.json`
- `high_pressure_60s_comparison.json`
- `opening.pt`
- `staged.pt`
