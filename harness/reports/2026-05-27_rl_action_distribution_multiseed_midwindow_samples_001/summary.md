# Action Distribution Multiseed Midwindow Samples

## 结论

- Gate decision: `repair_samples_exported_not_policy_gate`
- Source checkpoint: `harness/reports/2026-05-27_rl_action_distribution_regularization_opening_ablation_001/per_map_uniform_0_2/staged.pt`
- Related failures: `fail_20260527_046`, `fail_20260527_047`
- Sample path: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/soda_midwindow_45_100_route_recovery_samples.jsonl`

本轮按上一轮 phase-split retrain 的结论扩展 `soda-creek` 中窗数据覆盖：使用 `per_map_uniform_0_2` staged checkpoint 跑 `62400-62419` 共 20 个 seed 的 180 秒评估，并只保存失败局 sampled traces。导出的 `45-100s` route recovery repair samples 从单 seed `51` 条扩展到 4 seed `389` 条，validator 判定有效。

这仍然只是 repair training input，不是 RL policy gate。当前 policy 在 20 seed `soda-creek` 180 秒评估中 win rate 只有 `0.1`，说明 `soda-creek` 中窗和长窗问题仍然存在。

## Source Evaluation

- Map: `soda-creek`
- Seeds: `62400-62419`
- Seconds: `180`
- Win rate: `0.1`
- Average survival: `62.3758s`
- Damage taken average: `115.2353`
- Trace stride: `10`
- Trace failed only: `true`
- Trace include observation: `true`
- Failed trace files: `18`

20 个 seed 中只有 2 局没有写入 failed-only trace；多数失败仍发生在 45 秒前，能贡献 `45-100s` repair samples 的 seed 为 `62404`、`62406`、`62410` 和 `62414`。

## Export

- Decision: `route_recovery_samples_exported`
- Source traces: `18`
- Inspected trace rows: `2688`
- Negative route recovery rows: `415`
- Boundary hotspot rows: `396`
- Exported samples: `389`
- Time range: `45.3330s-99.9988s`
- Phase duration conditioning: `300s`

| Distribution | Counts |
| --- | --- |
| Map | `{"soda-creek": 389}` |
| Seeds | `62404`, `62406`, `62410`, `62414` |
| Original actions | `{"1": 287, "6": 58, "2": 27, "3": 17}` |
| Target actions | `{"5": 251, "3": 68, "2": 42, "7": 17, "1": 11}` |
| Target labels | `{"geometry_inward_non_wallward_action": 289, "highest_scored_non_wallward_action": 100}` |

`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，0 error、0 warning。

## Phase Dry Runs

| Phase | Samples | Edge recovery samples | Soft recovery samples | Time range |
| --- | ---: | ---: | ---: | --- |
| `opening 45-60s` | `5502` | `114` | `114` | `0.0s-59.9994s` |
| `mid 60-100s` | `10192` | `281` | `281` | `60.3328s-179.6761s` |

Dry-run 已启用 `--recovery-soft-target top_k_scores` 与 `--action-distribution-regularization 0.2 --action-distribution-target per_map_uniform_present`。本轮最值得继续的是 mid-only 消融：`60-100s` 中窗 soft recovery 样本从上一轮 `24` 条提升到 `281` 条，且不需要重新碰 opening 子模型。

## 判断

- 数据覆盖相对上一轮明显改善，但仍只来自 4 个能活过中窗的失败 seed。
- `45-60s` opening 样本不应直接重训 opening；上一轮已经证明重训 opening 会破坏多图短窗动作分布。
- 下一步应优先用 `60-100s` 的 `281` 条 mid recovery samples 做 mid-only staged 消融，并保留 `per_map_uniform_0_2` opening 子模型。
- 如果 mid-only 仍不能改善 `soda-creek` 180 秒，应继续扩大失败 trace seeds 或引入非贴边危险状态样本，而不是继续提高 recovery weight。

## 输出文件

- `soda_180s_trace_eval.json`
- `traces/*.json`
- `export_report.json`
- `export_report.md`
- `soda_midwindow_45_100_route_recovery_samples.jsonl`
- `sample_validation.json`
- `sample_validation.md`
- `mixed_opening_45_60_dry_run.json`
- `mixed_mid_dry_run.json`
