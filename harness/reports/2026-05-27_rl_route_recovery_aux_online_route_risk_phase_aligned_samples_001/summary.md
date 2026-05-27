# Route Recovery Aux Online Route Risk Phase-Aligned Samples

## 结论

- Gate decision: `dataset_validated_not_training_gate`
- Source traces: `3` failed `soda-creek` traces from `no_class_weight_2_0`
- Time window: `20-47s`
- Phase duration conditioning: `300s`
- Exported samples: `143`
- Validation: `edge_recovery_samples_valid`

这批样本复用 `online_route_risk_samples` 的来源，但在写出 observation 前按 `time_seconds / 300` 重写 normalized progress。这样 `20-47s` 的失败在线样本会落在 staged opening 的 `0-60s` 长窗里，而不会被 `time_phase_filter opening` 错误过滤。

## Export

- Inspected trace rows: `340`
- Outside time window rows: `180`
- Negative route_recovery rows: `143`
- Boundary hotspot rows: `143`
- Missing observation rows: `0`
- Original actions: action `6` `79`，action `5` `41`，action `1` `23`
- Target actions: action `2` `102`，action `1` `17`，action `3` `16`，action `5` `7`，action `7` `1`
- Target labels: `geometry_inward_non_wallward_action` `126`，`highest_scored_non_wallward_action` `17`

## Mixed Opening Dry Run

与原多图 boundary samples 和三图 phase-aligned KiteBot 轨迹混合后：

- Opening sample count: `5760`
- Edge recovery samples: `372`
- Edge recovery ratio: `0.0646`
- Map distribution: `soda-creek` `0.3474`，`caramel-workshop` `0.3309`，`cracked-star-jar` `0.3217`
- Overall target action `2` ratio: `0.1052`

## 判断

phase-duration conditioning 修复了 raw online samples 不能进入 opening phase filter 的问题。虽然该批样本自身 target action `2` 占 `0.7133`，但混入完整 opening 训练集后整体 action `2` ratio 只有 `0.1052`，可用于低权重训练消融。它仍只是 repair training input，不是 policy gate。

下一步训练必须：

- 保留 `class_weighting = none`
- 使用低权重或默认权重，不放大这批样本
- 训练后只跑 60 秒 high-pressure 三图 deterministic gate
- 不能把单次短窗改善当作 stage 03 或 RL acceptance

## 输出文件

- `online_route_risk_phase_aligned_samples.jsonl`
- `export_report.json`
- `export_report.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
- `mixed_opening_dry_run.json`
