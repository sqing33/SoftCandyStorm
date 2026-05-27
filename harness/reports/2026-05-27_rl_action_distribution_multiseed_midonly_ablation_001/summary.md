# Action Distribution Multiseed Mid-Only Ablation

## 结论

- Gate decision: `multiseed_midonly_ablation_recorded_needs_policy_repair`
- Source samples: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/soda_midwindow_45_100_route_recovery_samples.jsonl`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_regularization_opening_ablation_001/per_map_uniform_0_2/opening.pt`
- Failure case: `harness/failed_cases/fail_20260527_048_action_distribution_multiseed_midonly_gap.json`

本轮验证扩展后的 `60-100s` 多 seed midwindow repair samples 是否可以通过只替换 mid 子模型修复 `soda-creek` 180 秒失败。结果仍未通过：两个 mid-only 变体都保住了 60 秒短窗，但 180 秒 `soda-creek` 仍为 `0.0` win rate，并且 `cracked-star-jar` 180 秒降到 `0.4`。

## Variants

| Variant | Mid recovery weight | Mid soft recovery samples | 60s gate | 180s gate |
| --- | ---: | ---: | --- | --- |
| `mid_only_multiseed_w1` | `1.0` | `281` | `multimap_comparison_recorded_not_balance_gate` | `multimap_comparison_recorded_needs_policy_repair` |
| `mid_only_multiseed_w4` | `4.0` | `281` | `multimap_comparison_recorded_not_balance_gate` | `multimap_comparison_recorded_needs_policy_repair` |

## 60s High-Pressure

| Variant | Soda win | Caramel win | Cracked win | Repair maps |
| --- | ---: | ---: | ---: | --- |
| `mid_only_multiseed_w1` | `0.4` | `0.8` | `0.8` | none |
| `mid_only_multiseed_w4` | `0.4` | `0.8` | `0.8` | none |

这说明保留 `per_map_uniform_0_2` opening 子模型是正确的：只替换 mid 没有重演上一轮 phase-split opening 重训导致的 60 秒 action-bias repair。

## 180s High-Pressure

| Variant | Soda win | Soda avg survival | Caramel win | Cracked win | Dominant tendency |
| --- | ---: | ---: | ---: | ---: | --- |
| `mid_only_multiseed_w1` | `0.0` | `57.3273s` | `0.8` | `0.4` | soda action `3`, cracked action `5` |
| `mid_only_multiseed_w4` | `0.0` | `61.6816s` | `0.8` | `0.4` | soda action `3`, cracked action `5` |

`w4` 相比上一轮单 seed mid-only 只把 `soda-creek` 平均存活小幅抬高，但没有转化为胜率；同时两个权重都让 `cracked-star-jar` 180 秒回落到 `0.4`。因此新增样本证明了失败面，而不是提供可推进的 policy candidate。

## 判断

- `281` 条 mid soft recovery samples 仍不足以修复 `soda-creek` 180 秒长窗。
- 单纯边界顶墙样本会把 mid 行为推向局部撤离动作，无法覆盖非贴边危险状态、升级后目标或长期路线规划。
- 下一步不应继续提高 recovery weight；更合理的是补充 `soda-creek` 45 秒前早死诊断、非贴边危险状态样本，或做 per-map/per-phase target 消融。
- 这些 checkpoint 不得进入 stage 03、300 秒长窗或 RL acceptance。

## 输出文件

- `mid_only_multiseed_w1/mid_training.json`
- `mid_only_multiseed_w1/packaging.json`
- `mid_only_multiseed_w1/staged.pt`
- `mid_only_multiseed_w1/high_pressure_60s_comparison.json`
- `mid_only_multiseed_w1/high_pressure_180s_comparison.json`
- `mid_only_multiseed_w4/mid_training.json`
- `mid_only_multiseed_w4/packaging.json`
- `mid_only_multiseed_w4/staged.pt`
- `mid_only_multiseed_w4/high_pressure_60s_comparison.json`
- `mid_only_multiseed_w4/high_pressure_180s_comparison.json`
