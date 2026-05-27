# Action Distribution Opening Action3 Low-Weight Ablation

## 结论

- Gate decision: `opening_action3_low_weight_ablation_recorded_needs_late_policy_repair`
- Variant: `opening_action3_w0_5_windowed`
- Source samples: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_samples_001/soda_opening_20_45_action3_route_recovery_samples.jsonl`
- Base mid/late: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt` / `late.pt`
- Failure case: `harness/failed_cases/fail_20260527_049_action_distribution_opening_action3_late_gap.json`

本轮使用 `20-45s` opening action `3` repair samples 做低权重 opening retention 消融。`opening_action3_w0_5_windowed` 保留了 `per_map_uniform_present` 动作分布正则，并把 repair sample 权重降到 `0.5`；训练时只保留 `20-45s` 的 edge recovery rows，避免旧 opening repair samples 污染口径。

结果是阶段性有效但不能推进：60 秒 hard gate 与 180 秒探针都没有 repair map，`soda-creek` 180 秒 win rate 从上一轮 `0.0` 提升到 `0.6`。但 300 秒高压三图仍全部 `0.0` 胜率，因此该 checkpoint 不能进入 stage 03、RL acceptance 或任何 release/playtest 结论。

## Training

| Variant | Edge weight | Window | Samples | Soft recovery samples | Validation accuracy | Validation entropy |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `opening_action3_w0_5_windowed` | `0.5` | `20-45s` | `6112` | `724` | `0.5393` | `1.368171` |

训练集 mix：

- `soda-creek`: `40.85%`
- `caramel-workshop`: `29.58%`
- `cracked-star-jar`: `29.56%`
- `edge_recovery_supervision`: `11.85%`
- `trajectory`: `88.15%`

`sample_weights` 为 `edge_recovery_auxiliary`，权重范围 `0.5-1.0`，均值 `0.941513`。这说明 repair rows 被降权，而不是继续放大 `soda-creek` opening 样本占比。

## 60s High-Pressure

| Map | Win rate | Avg survival | Dominant action | Normalized entropy | Inner gate |
| --- | ---: | ---: | --- | ---: | --- |
| `soda-creek` | `0.4` | `45.6796s` | action `3` `0.4101` | `0.6251` | `comparison_recorded_not_balance_gate` |
| `caramel-workshop` | `1.0` | `60.0328s` | action `3` `0.4553` | `0.6196` | `comparison_recorded_not_balance_gate` |
| `cracked-star-jar` | `0.8` | `56.2862s` | action `5` `0.4716` | `0.5149` | `comparison_recorded_not_balance_gate` |

60 秒 overall gate 为 `multimap_comparison_recorded_not_balance_gate`，`repair_maps` 为空。相比 `per_map_uniform_0_2`，`soda-creek` action `3` ratio 从 `0.6696` 降到 `0.4101`，`caramel-workshop` win rate 从 `0.8` 提升到 `1.0`。

## 180s High-Pressure

| Map | Win rate | Avg survival | Dominant action | Normalized entropy | Inner gate |
| --- | ---: | ---: | --- | ---: | --- |
| `soda-creek` | `0.6` | `121.8790s` | action `1` `0.5044` | `0.6660` | `comparison_recorded_not_balance_gate` |
| `caramel-workshop` | `1.0` | `180.0095s` | action `1` `0.3875` | `0.7448` | `comparison_recorded_not_balance_gate` |
| `cracked-star-jar` | `0.8` | `152.2675s` | action `1` `0.5215` | `0.6348` | `comparison_recorded_not_balance_gate` |

180 秒 overall gate 为 `multimap_comparison_recorded_not_balance_gate`，`repair_maps` 为空。这是本轮的主要正向信号：opening action `3` 低权重修复让先前 `soda-creek` 180 秒 `0.0` 胜率缺口得到明显缓解。

## 300s High-Pressure

| Map | Win rate | Avg survival | Dominant action | Normalized entropy | Inner gate |
| --- | ---: | ---: | --- | ---: | --- |
| `soda-creek` | `0.0` | `143.2769s` | action `1` `0.5533` | `0.6385` | `comparison_recorded_not_balance_gate` |
| `caramel-workshop` | `0.0` | `218.5377s` | action `1` `0.4211` | `0.7291` | `comparison_recorded_not_balance_gate` |
| `cracked-star-jar` | `0.0` | `183.7876s` | action `1` `0.5847` | `0.5966` | `comparison_recorded_not_balance_gate` |

300 秒 overall gate 为 `multimap_comparison_recorded_needs_policy_repair`，`repair_maps = ["soda-creek", "caramel-workshop", "cracked-star-jar"]`。失败已经从 opening action `3` 顶墙转移为中后期 action `1` 倾向与 late survival 缺口。

## 判断

- `20-45s` opening action `3` 样本是有效修复输入，低权重 + per-map action-distribution regularization 可以改善短中窗。
- 这不是完整 RL policy repair：300 秒三图仍全 0%，不能推进 stage 03、300 秒 acceptance、playtest 或 release。
- 下一步应保留该 opening 子模型作为较强 opening baseline，再针对 `180-300s` late survival、升级后目标选择、Boss/hazard pressure 和 action `1` late drift 做失败 trace 诊断。

## 输出文件

- `opening_action3_w0_5_windowed/opening_training.json`
- `opening_action3_w0_5_windowed/opening.pt`
- `opening_action3_w0_5_windowed/packaging.json`
- `opening_action3_w0_5_windowed/staged.pt`
- `opening_action3_w0_5_windowed/high_pressure_60s_comparison.json`
- `opening_action3_w0_5_windowed/high_pressure_180s_comparison.json`
- `opening_action3_w0_5_windowed/high_pressure_300s_comparison.json`
