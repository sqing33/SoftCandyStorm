# Action Distribution Regularization Opening Ablation

## 结论

- Gate decision: `ablation_recorded_short_window_repair_long_window_gap`
- Feature: `--action-distribution-regularization`
- Target mode: `per_map_uniform_present`
- Recovery soft target: `top_k_scores`
- Failure case: `harness/failed_cases/fail_20260527_046_action_distribution_regularization_opening_long_window_gap.json`

本轮先给 behavior clone 训练加入显式动作分布正则，再用 `soft_topk_0_6` 路线重训 opening 子模型。`per_map_uniform_0_2` 能把 60 秒三图的 action-bias repair 降下来，但 180 秒 `soda-creek` 仍为 `0.0` 胜率，所以不能推进 stage 03、300 秒评估或 RL acceptance。

## Training

| Variant | Coefficient | Validation accuracy | Validation entropy | Validation action distribution loss |
| --- | ---: | ---: | ---: | ---: |
| `per_map_uniform_0_05` | `0.05` | `0.5469` | `1.443633` | `0.015971` |
| `per_map_uniform_0_2` | `0.20` | `0.5486` | `1.447550` | `0.015165` |

两档都使用 `entropy_regularization = 0.01`、`recovery_soft_target = top_k_scores`、`primary_mass = 0.6`，并在每张地图内把训练集中出现过的 8 个移动动作作为 uniform-present target。

## 60s High-Pressure Comparison

| Variant | Map | Win rate | Avg survival | Dominant action | Normalized entropy | Inner gate |
| --- | --- | ---: | ---: | --- | ---: | --- |
| `per_map_uniform_0_05` | `soda-creek` | `0.4` | `42.4930s` | action `3` `0.6690` | `0.4361` | `comparison_recorded_not_balance_gate` |
| `per_map_uniform_0_05` | `caramel-workshop` | `0.8` | `54.8128s` | action `3` `0.7561` | `0.4146` | `comparison_recorded_needs_action_bias_repair` |
| `per_map_uniform_0_05` | `cracked-star-jar` | `0.8` | `53.4862s` | action `3` `0.6078` | `0.5259` | `comparison_recorded_not_balance_gate` |
| `per_map_uniform_0_2` | `soda-creek` | `0.4` | `42.7797s` | action `3` `0.6696` | `0.4366` | `comparison_recorded_not_balance_gate` |
| `per_map_uniform_0_2` | `caramel-workshop` | `0.8` | `54.8128s` | action `3` `0.6562` | `0.4449` | `comparison_recorded_not_balance_gate` |
| `per_map_uniform_0_2` | `cracked-star-jar` | `0.8` | `53.4862s` | action `3` `0.6068` | `0.5089` | `comparison_recorded_not_balance_gate` |

`per_map_uniform_0_2` 的 60 秒 overall gate 为 `multimap_comparison_recorded_not_balance_gate`，`repair_maps` 为空；它主要修掉了 `caramel-workshop` 的 action `3` dominant repair，但没有提升 `soda-creek` 胜率。

## 180s Probe

| Map | Win rate | Avg survival | Dominant action | Normalized entropy | Inner gate |
| --- | ---: | ---: | --- | ---: | --- |
| `soda-creek` | `0.0` | `52.6997s` | action `3` `0.5245` | `0.6375` | `comparison_recorded_not_balance_gate` |
| `caramel-workshop` | `0.8` | `150.7942s` | action `1` `0.5271` | `0.5840` | `comparison_recorded_not_balance_gate` |
| `cracked-star-jar` | `0.4` | `124.1099s` | action `1` `0.5266` | `0.5557` | `comparison_recorded_not_balance_gate` |

180 秒 overall gate 为 `multimap_comparison_recorded_needs_policy_repair`，`repair_maps = ["soda-creek"]`。这说明 per-map 动作分布正则能缓解 deterministic action collapse，但不能解决 `soda-creek` 的长窗路线恢复和目标选择问题。

## 判断

显式动作分布正则是有效的训练工具：相比单独提高 entropy，它更直接地影响在线 deterministic action ratio，并能消除 60 秒 compare 内部的 action-bias repair。但它仍是分布级约束，不知道哪些状态需要路线恢复、升级选择或阶段目标切换，因此不能单独作为 movement policy 修复。

下一步应基于 `soda-creek` 180 秒失败 trace 做状态条件化修复：导出 `50-80s` 路线恢复 / 升级后目标样本，或把 route recovery reward profile 纳入 closed-loop PPO / curriculum，而不是继续只提高分布正则系数。

## 输出文件

- `per_map_uniform_0_05/opening_training.json`
- `per_map_uniform_0_05/opening.pt`
- `per_map_uniform_0_05/packaging.json`
- `per_map_uniform_0_05/staged.pt`
- `per_map_uniform_0_05/high_pressure_60s_comparison.json`
- `per_map_uniform_0_2/opening_training.json`
- `per_map_uniform_0_2/opening.pt`
- `per_map_uniform_0_2/packaging.json`
- `per_map_uniform_0_2/staged.pt`
- `per_map_uniform_0_2/high_pressure_60s_comparison.json`
- `per_map_uniform_0_2/high_pressure_180s_comparison.json`
