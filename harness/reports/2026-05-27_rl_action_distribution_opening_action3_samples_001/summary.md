# Action Distribution Opening Action3 Samples

## 结论

- Gate decision: `repair_samples_exported_not_policy_gate`
- Source traces: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/traces`
- Source diagnostic: `harness/reports/2026-05-27_rl_action_distribution_soda_failure_distribution_001/summary.md`
- Sample path: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_samples_001/soda_opening_20_45_action3_route_recovery_samples.jsonl`

本轮按失败分布诊断导出 `soda-creek` opening 早死修复样本：只保留 `20-45s`、负 `route_recovery`、贴边且原始动作继续为 action `3` 的 sampled trace rows。导出成功，样本覆盖 18 个失败 seed，可作为下一轮 opening retention 消融的训练输入。

这仍不是 policy gate。上一轮已经证明粗暴 opening 重训会破坏多图短窗动作分布，因此该样本包只能用于低权重、per-map 受控、并必须先过 60 秒三图 hard gate 的消融。

## Export

- Decision: `route_recovery_samples_exported`
- Source traces: `18`
- Inspected trace rows: `2688`
- Negative route recovery rows in time window: `628`
- Boundary hotspot rows: `619`
- Original action filtered rows: `17`
- Exported samples: `587`
- Time range: `20.0000s-44.9997s`
- Phase duration conditioning: `300s`
- Original action filter: `3`

| Distribution | Counts |
| --- | --- |
| Map | `{"soda-creek": 587}` |
| Original actions | `{"3": 587}` |
| Target actions | `{"5": 262, "7": 205, "8": 95, "1": 25}` |
| Target labels | `{"geometry_inward_non_wallward_action": 298, "highest_scored_non_wallward_action": 289}` |

`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，0 error、0 warning。

## Opening Dry Run

- Dataset samples after opening filter: `6112`
- Edge recovery samples after opening filter: `724`
- Soft recovery samples: `724`
- Sample source mix: `edge_recovery_supervision 11.85%`, `trajectory 88.15%`
- Map mix: `soda-creek 40.85%`, `caramel-workshop 29.58%`, `cracked-star-jar 29.56%`
- Gate decision: `dataset_validated_not_training_gate`

该 dry-run 说明样本可进入 behavior clone 训练，但 `soda-creek` 比例被明显抬高。下一步如果训练 opening，必须使用低 `edge-recovery-sample-weight`，保留 `per_map_uniform_present` action-distribution regularization，并先跑 60 秒三图 hard gate。

## 输出文件

- `export_report.json`
- `export_report.md`
- `soda_opening_20_45_action3_route_recovery_samples.jsonl`
- `sample_validation.json`
- `sample_validation.md`
- `mixed_opening_dry_run.json`
