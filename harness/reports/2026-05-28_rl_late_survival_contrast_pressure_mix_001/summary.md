# Late Survival Contrast + Pressure Mix

## 结论

- Gate decision: `late_survival_contrast_pressure_mix_recorded_needs_closed_loop_repair`
- Variant: `late_contrast_pressure`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- Base mid: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt`
- New late: `late_contrast_pressure/late.pt`
- Failure case: `harness/failed_cases/fail_20260528_063_late_survival_contrast_pressure_mix_gap.json`

本轮不再单纯堆叠 adapter-derived late pressure rows，而是把 `2026-05-27_rl_rule_bot_late_survival_trajectory_001` 中的真实 180-300 秒 survival / near-failure trajectory 作为对照数据加入，并继续保留 `phase_aligned` KiteBot late trajectory、`risk_recovery_samples_clean` 与 `late_boundary_recovery_samples`。`late_boundary` rows 权重降到 `0.25`，`risk_recovery` rows 权重为 `0.5`，评估固定为 no-ranker parity。

结果仍为 repair：60 秒为 `0.4/1.0/0.8`，180 秒为 `0.6/1.0/0.8`，300 秒为 `0.0/0.2/0.2`。相比上一轮 `pressure_late_w0_5` no-ranker，`caramel-workshop` 300 秒从 `0.0` 到 `0.2`，但 `soda-creek` 仍为 `0.0`，`cracked-star-jar` 仍为 `0.2`，不能推进 stage 03、RL acceptance、playtest 或 release。

## Dataset

| Metric | Value |
| --- | ---: |
| Total late samples | `20931` |
| Trajectory samples | `19153` |
| Edge recovery samples | `1076` |
| Risk recovery samples | `702` |
| Average health ratio | `0.6507` |

Map distribution:

| Map | Samples | Ratio |
| --- | ---: | ---: |
| `soda-creek` | `6844` | `32.70%` |
| `caramel-workshop` | `7132` | `34.07%` |
| `cracked-star-jar` | `6955` | `33.23%` |

Dry-run 没有触发 sequence diagnosis warning。Repair rows 的有效采样占比被压低到 edge `5.30%`、risk `3.33%`，避免本轮变成另一个高权重局部离边样本消融。

## Training

| Phase | Samples | Edge samples | Risk samples | Validation accuracy | Validation entropy |
| --- | ---: | ---: | ---: | ---: | ---: |
| `late` | `20931` | `1076` | `702` | `0.6570` | `1.189526` |

训练使用 GRU context8、map one-hot、time phase one-hot、`danger_action_change` sample weighting、soft recovery targets、`entropy_regularization=0.02` 和 `action_distribution_regularization=0.2 / per_map_uniform_present`。

## No-ranker Parity Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_watch` |
| `180s` | `0.6` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.2` | `0.2` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `150.2383s` | opening `2`, late `3` | action `1` `51.43%` | `0.6857` |
| `caramel-workshop` | `0.2` | `234.4904s` | late `4` | action `1` `33.03%` | `0.7908` |
| `cracked-star-jar` | `0.2` | `202.4542s` | opening `1`, late `3` | action `1` `49.89%` | `0.6712` |

相比上一轮 `pressure_late_w0_5` no-ranker，`soda-creek` 平均存活从 `144.1837s` 小幅提升到 `150.2383s`，`caramel-workshop` 从 `220.1047s` 提升到 `234.4904s` 并出现 1 个 300 秒胜局，但 `cracked-star-jar` 从 `212.7624s` 回落到 `202.4542s`。失败仍集中在 late，并且 `soda-creek` / `cracked-star-jar` 仍有 opening death。

## 判断

- Real trajectory contrast improves dataset balance and gives `caramel-workshop` a small long-window gain, but it is still not enough for cross-map 300 秒 survival.
- Late-only offline imitation remains action `1` dominant in long-window failures.
- The next repair should move to closed-loop late survival curriculum or a joint retention objective that includes soda opening retention plus late route / low-health / hazard / Boss recovery.
- Any further candidate must keep no-ranker parity reports for comparison; upgrade ranker may be diagnostic only.

## 输出文件

- `late_contrast_pressure_dry_run.json`
- `late_contrast_pressure/late_training.json`
- `late_contrast_pressure/late.pt`
- `late_contrast_pressure/packaging.json`
- `late_contrast_pressure/staged.pt`
- `late_contrast_pressure/high_pressure_60s_comparison.json`
- `late_contrast_pressure/high_pressure_180s_comparison.json`
- `late_contrast_pressure/high_pressure_300s_comparison.json`
- `late_contrast_pressure/failure_analysis_300s.json`
- `late_contrast_pressure/failure_analysis_300s.md`
