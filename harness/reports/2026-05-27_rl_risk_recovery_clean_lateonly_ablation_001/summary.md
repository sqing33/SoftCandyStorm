# Clean Risk Recovery Late-Only Ablation

## 结论

- Gate decision: `clean_risk_lateonly_ablation_recorded_needs_closed_loop_late_repair`
- Variant: `clean_late_w0_5`
- Clean sample source: `harness/reports/2026-05-27_rl_risk_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- Base mid: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt`
- New late: `clean_late_w0_5/late.pt`
- Failure case: `harness/failed_cases/fail_20260527_061_clean_risk_lateonly_gap.json`

本轮只替换 late 子模型：保留 `opening_action3_w0_5_windowed` opening 和原 `route_recovery_aux_entropy_retry` mid，把 raw 780 条 late adapter rows 换成 702 条 clean risk recovery rows，并将 `risk_recovery_sample_weight` 从上一轮 raw w4 的 `4.0` 降到 `0.5`。训练仍使用 GRU context8、map one-hot、time phase one-hot、late filter、class weighting、danger_action_change、soft target、entropy regularization 和 per-map action distribution regularization。

结果仍是 repair：60 秒和 180 秒 regression 保住，但 300 秒三图全为 `0.0` 胜率。clean rows 让 `soda-creek` 与 `caramel-workshop` 平均存活略高于 raw w4，代价是 `cracked-star-jar` 从 raw w4 的 `0.2` 胜率回落到 `0.0`。这说明去掉可疑 adapter rows 能改善部分长窗存活，但不能解决 180-300 秒闭环生存，也不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Variant | Samples | Risk samples | Weight | Validation accuracy | Validation entropy | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `clean_late_w0_5` | `13972` | `702` | `0.5` | `0.7749` | `0.721445` | `behavior_clone_smoke_only_not_policy_gate` |

训练样本分布：

- `trajectory`: `13270`
- `risk_recovery_supervision`: `702`
- `soda-creek`: `41.74%`
- `cracked-star-jar`: `35.96%`
- `caramel-workshop`: `22.29%`

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Comparison Against Raw w4

| Map | Clean win | Clean avg survival | Raw w4 win | Raw w4 avg survival | Clean dominant action |
| --- | ---: | ---: | ---: | ---: | --- |
| `soda-creek` | `0.0` | `149.0248s` | `0.0` | `144.1104s` | action `1` `46.68%` |
| `caramel-workshop` | `0.0` | `223.1454s` | `0.0` | `215.6304s` | action `1` `32.64%` |
| `cracked-star-jar` | `0.0` | `197.4302s` | `0.2` | `208.1221s` | action `1` `45.95%` |

## Failure Analysis

`failure_analysis_300s.md` 记录 15/15 失败：

- `soda-creek`: 2 条 opening 早死，3 条 late 失败。
- `caramel-workshop`: 5 条全部 late 失败。
- `cracked-star-jar`: 1 条 opening 早死，4 条 late 失败。

## 判断

- Clean filter 是有价值的数据卫生步骤，但 low-weight clean late-only imitation 仍不能把长窗 late survival 转成胜率。
- 下一步不应继续只调同一批 adapter-derived late samples 的权重；更值得推进的是 closed-loop late survival/curriculum、升级选择后的目标规划、或针对 180-300 秒失败种子的在线 reward / route objective。
- 任一后续候选仍必须保留 60 秒 hard gate、180 秒 regression 和 300 秒三图 deterministic comparison。

## 输出文件

- `clean_late_w0_5/late_training.json`
- `clean_late_w0_5/late.pt`
- `clean_late_w0_5/packaging.json`
- `clean_late_w0_5/staged.pt`
- `clean_late_w0_5/high_pressure_60s_comparison.json`
- `clean_late_w0_5/high_pressure_180s_comparison.json`
- `clean_late_w0_5/high_pressure_300s_comparison.json`
- `clean_late_w0_5/failure_analysis_300s.json`
- `clean_late_w0_5/failure_analysis_300s.md`
