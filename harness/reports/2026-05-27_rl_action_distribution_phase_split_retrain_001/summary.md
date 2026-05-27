# Action Distribution Phase Split Retrain

## 结论

- Gate decision: `phase_split_retrain_recorded_needs_more_multiseed_midwindow_data`
- Source samples: `harness/reports/2026-05-27_rl_action_distribution_regularization_soda_midwindow_samples_001/soda_midwindow_route_recovery_samples.jsonl`
- Failure case: `harness/failed_cases/fail_20260527_047_action_distribution_phase_split_retrain_tradeoff.json`

本轮验证了 `50-80s` repair samples 的 phase-split 用法：`50-60s` 进入 opening，`60-80s` 进入 mid。结果显示单 seed 的窄样本不足以修复 `soda-creek` 180 秒长窗；重训 opening 还会破坏 60 秒短窗动作分布。因此该路线不能推进 stage 03、300 秒评估或 RL acceptance。

## Variants

| Variant | Opening | Mid | Edge recovery weight | 60s gate | 180s gate |
| --- | --- | --- | ---: | --- | --- |
| `phase_split_soda_mid` | retrained with `50-60s` samples | retrained with `60-80s` samples | `4.0` mid | `multimap_comparison_recorded_needs_policy_repair` | `multimap_comparison_recorded_watch` |
| `mid_only_soda_mid` | previous `per_map_uniform_0_2` | retrained with `60-80s` samples | `4.0` mid | `multimap_comparison_recorded_not_balance_gate` | `multimap_comparison_recorded_needs_policy_repair` |
| `mid_only_soda_mid_w16` | previous `per_map_uniform_0_2` | retrained with `60-80s` samples | `16.0` mid | `multimap_comparison_recorded_not_balance_gate` | `multimap_comparison_recorded_needs_policy_repair` |

## 60s High-Pressure

| Variant | Soda win | Caramel win | Cracked win | Repair maps |
| --- | ---: | ---: | ---: | --- |
| `phase_split_soda_mid` | `0.4` | `0.8` | `0.6` | `caramel-workshop`, `cracked-star-jar` |
| `mid_only_soda_mid` | `0.4` | `0.8` | `0.8` | none |
| `mid_only_soda_mid_w16` | `0.4` | `0.8` | `0.8` | none |

`phase_split_soda_mid` 说明 opening 重训不安全：它把 `caramel-workshop` action `3` ratio 推到 `0.8354`，`cracked-star-jar` action `3` ratio 推到 `0.7829`，重新触发 action-bias repair。

## 180s High-Pressure

| Variant | Soda win | Soda avg survival | Caramel win | Cracked win | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `phase_split_soda_mid` | `0.4` | `88.4904s` | `0.8` | `0.2` | `multimap_comparison_recorded_watch` |
| `mid_only_soda_mid` | `0.0` | `57.3273s` | `0.8` | `0.8` | `multimap_comparison_recorded_needs_policy_repair` |
| `mid_only_soda_mid_w16` | `0.0` | `57.3273s` | `0.8` | `0.6` | `multimap_comparison_recorded_needs_policy_repair` |

`phase_split_soda_mid` 把 `soda-creek` 从上一轮 `0.0` 拉到 `0.4`，但同时把 `cracked-star-jar` 从 `0.8` 拉低到 `0.2`，且 60 秒短窗出现 action-bias repair。`mid_only` 两档保住了 60 秒短窗，但没有修复 `soda-creek` 180 秒胜率。

## 判断

这轮结果支持两个结论：

- 不应继续用单 seed `50-80s` repair samples 直接重训 opening；它会破坏多图短窗动作分布。
- 单独重训 mid 即使把 24 条 `60-80s` 样本权重提高到 `16.0`，也只能小幅改变长窗动作分布，不能让 `soda-creek` 过 180 秒 gate。

下一步应扩大数据覆盖，而不是继续拧权重：用 `mid_only_soda_mid` 或 `per_map_uniform_0_2` 在 `soda-creek` 多 seed 导出 `45-100s` 失败 trace，收集更多 phase-aligned midwindow repair samples，再做 per-map / per-phase target 消融。

## 输出文件

- `phase_split_soda_mid/opening_training.json`
- `phase_split_soda_mid/mid_training.json`
- `phase_split_soda_mid/packaging.json`
- `phase_split_soda_mid/staged.pt`
- `phase_split_soda_mid/high_pressure_60s_comparison.json`
- `phase_split_soda_mid/high_pressure_180s_comparison.json`
- `mid_only_soda_mid/packaging.json`
- `mid_only_soda_mid/staged.pt`
- `mid_only_soda_mid/high_pressure_60s_comparison.json`
- `mid_only_soda_mid/high_pressure_180s_comparison.json`
- `mid_only_soda_mid_w16/mid_training.json`
- `mid_only_soda_mid_w16/packaging.json`
- `mid_only_soda_mid_w16/staged.pt`
- `mid_only_soda_mid_w16/high_pressure_60s_comparison.json`
- `mid_only_soda_mid_w16/high_pressure_180s_comparison.json`
