# Opening Action3 Late-Only Risk Recovery Ablation

## 结论

- Gate decision: `lateonly_ablation_recorded_needs_closed_loop_late_repair`
- Variant: `late_risk_current_w4`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- Base mid: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt`
- New late: `late_risk_current_w4/late.pt`
- Failure case: `harness/failed_cases/fail_20260527_050_opening_action3_lateonly_gap.json`

本轮只重训 late 子模型：保留当前 opening action `3` 低权重子模型与原 mid 子模型，late 数据混合三图 phase-aligned 规则轨迹、late survival clean teacher 轨迹，以及当前 checkpoint 导出的 `780` 条 `risk_recovery_supervision_sample`。

结果说明 late-only imitation 仍不足：60 秒 hard gate 和 180 秒 regression 均保住，但 300 秒三图仍为 repair；`cracked-star-jar` 从 `0.0` 提到 `0.2`，`soda-creek` 与 `caramel-workshop` 仍为 `0.0`。

## Training

| Variant | Samples | Risk samples | Validation accuracy | Validation entropy | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `late_risk_current_w4` | `14050` | `780` | `0.7740` | `0.736441` | `behavior_clone_smoke_only_not_policy_gate` |

训练设置：

- `architecture=gru`
- `context_frames=8`
- `map_conditioning=one_hot`
- `time_phase_conditioning=one_hot`
- `time_phase_filter=late`
- `class_weighting=inverse_frequency`
- `sample_weighting=danger_action_change`
- `risk_recovery_sample_weight=4.0`
- `recovery_soft_target=top_k_scores`
- `entropy_regularization=0.02`
- `action_distribution_regularization=0.2`
- `action_distribution_target=per_map_uniform_present`

训练样本分布：

- `trajectory`: `13270`
- `risk_recovery_supervision`: `780`
- `soda-creek`: `41.56%`
- `cracked-star-jar`: `36.27%`
- `caramel-workshop`: `22.17%`

## 60s / 180s Regression

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |

这说明只替换 late 子模型没有破坏当前 opening/mid baseline。

## 300s Probe

| Map | Win rate | Avg survival | Dominant action | Entropy | Inner gate |
| --- | ---: | ---: | --- | ---: | --- |
| `soda-creek` | `0.0` | `144.1104s` | action `1` `0.4839` | `0.7360` | `comparison_recorded_not_balance_gate` |
| `caramel-workshop` | `0.0` | `215.6304s` | action `1` `0.3334` | `0.8453` | `comparison_recorded_not_balance_gate` |
| `cracked-star-jar` | `0.2` | `208.1221s` | action `1` `0.4400` | `0.7311` | `comparison_recorded_not_balance_gate` |

300 秒 overall gate 为 `multimap_comparison_recorded_needs_policy_repair`，`repair_maps = ["soda-creek", "caramel-workshop"]`，并且 `cracked-star-jar` 仍低于 KiteBot。

## Failure Analysis

`failure_analysis_300s.md` 显示 `14` 条失败中：

- `soda-creek`: `2` 条 opening 早死，`3` 条 late 失败。
- `caramel-workshop`: `5` 条全部 late 失败。
- `cracked-star-jar`: `1` 条 opening 早死，`3` 条 late 失败。

late 子模型把 action entropy 提高了，但没有把 late survival 转成稳定胜率。继续堆离线 risk samples 的收益有限，下一步应改成 closed-loop late survival / curriculum，或者加入升级后目标选择和路线规划约束。

## 输出文件

- `late_risk_current_w4/late_training.json`
- `late_risk_current_w4/late.pt`
- `late_risk_current_w4/packaging.json`
- `late_risk_current_w4/staged.pt`
- `late_risk_current_w4/high_pressure_60s_comparison.json`
- `late_risk_current_w4/high_pressure_180s_comparison.json`
- `late_risk_current_w4/high_pressure_300s_comparison.json`
- `late_risk_current_w4/failure_analysis_300s.json`
- `late_risk_current_w4/failure_analysis_300s.md`
