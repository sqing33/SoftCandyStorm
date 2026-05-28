# Expanded Late Pressure Late-only Ablation

## 结论

- Gate decision: `late_pressure_expanded_lateonly_ablation_recorded_needs_fallback_repair`
- Variant: `pressure_late_w0_5`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- Base mid: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt`
- New late: `pressure_late_w0_5/late.pt`
- Failure case: `harness/failed_cases/fail_20260528_062_late_pressure_expanded_lateonly_gap.json`

本轮只替换 late 子模型：保留已知 opening 和 mid 基线，用 `1076` 条 expanded late boundary edge rows、`702` 条 clean risk recovery rows 和 `13270` 条 late/phase-aligned rule-bot trajectory rows 训练新的 late GRU context8 子模型。训练使用 `edge_recovery_sample_weight=0.5`、`risk_recovery_sample_weight=0.5`、soft target、entropy regularization 和 `per_map_uniform_present` 动作分布正则。

结果仍为 repair：60 秒短窗保持并提升到 `0.8/1.0/1.0`，300 秒 `cracked-star-jar` 保持 `0.4`，但 `soda-creek` 和 `caramel-workshop` 300 秒仍为 `0.0`；同时 `caramel-workshop` 180 秒从上一轮 late-boundary ablation 的 `1.0` 回落到 `0.2`。该 checkpoint 不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Phase | Samples | Edge samples | Risk samples | Validation accuracy | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `late` | `15048` | `1076` | `702` | `0.5924` | `behavior_clone_smoke_only_not_policy_gate` |

训练样本分布：

- `trajectory`: `13270`
- `edge_recovery_supervision`: `1076`
- `risk_recovery_supervision`: `702`
- Target action `8`: `2350 / 15048` (`15.62%`) after mixing with trajectories

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.8` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6` | `0.2` | `1.0` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.4` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `168.0020s` | opening `1`, mid `2`, late `2` | action `1` `54.91%` | `0.6357` |
| `caramel-workshop` | `0.0` | `161.4553s` | mid `3`, late `2` | action `1` `48.50%` | `0.6621` |
| `cracked-star-jar` | `0.4` | `259.5771s` | late `3` | action `1` `42.94%` | `0.7508` |

相比上一轮 `late_boundary_w0_5`，该变体把 `soda-creek` 平均存活从 `156.1263s` 提到 `168.0020s`，把 `cracked-star-jar` 从 `222.3408s` 提到 `259.5771s`，但 `caramel-workshop` 从 `225.9526s` 回落到 `161.4553s`，并破坏了该地图的 180 秒 retention。

## 判断

- Expanded pressure samples are useful as diagnostic and repair input, but late-only imitation is still not enough for cross-map 300 秒 survival.
- Lowering both edge/risk weights to `0.5` avoided a pure action `8` collapse, but the staged policy still became action `1` dominant in long-window failures.
- Next repair should add a retention constraint or positive clean survival contrast, especially for `caramel-workshop`, before trying another late-only training pass.
- Any further candidate must rerun deterministic high-pressure `60 / 180 / 300` 秒 comparisons and keep failure cases updated.

## 输出文件

- `pressure_late_w0_5/late_training.json`
- `pressure_late_w0_5/late.pt`
- `pressure_late_w0_5/packaging.json`
- `pressure_late_w0_5/staged.pt`
- `pressure_late_w0_5/high_pressure_60s_comparison.json`
- `pressure_late_w0_5/high_pressure_180s_comparison.json`
- `pressure_late_w0_5/high_pressure_300s_comparison.json`
- `pressure_late_w0_5/failure_analysis_300s.json`
- `pressure_late_w0_5/failure_analysis_300s.md`
