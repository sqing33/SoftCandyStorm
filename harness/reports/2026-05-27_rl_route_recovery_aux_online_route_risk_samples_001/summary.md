# Route Recovery Aux Online Route Risk Samples

## 结论

- Gate decision: `dataset_validated_not_training_gate`
- Source traces: `3` failed `soda-creek` traces from `no_class_weight_2_0`
- Time window: `20-47s`
- Exported samples: `143`
- Validation: `edge_recovery_samples_valid`

这批样本来自 `no_class_weight_2_0` 的失败在线 trace：`soda-creek` seed `62400`、`62402`、`62403`。它只保留 `20-47s` 内 route_recovery 为负、boundary edge risk 高、原始动作继续顶边、目标动作不再顶边的帧。该批次用于后续 repair training input，不是策略修复证据。

## Export

- Inspected trace rows: `340`
- Outside time window rows: `180`
- Negative route_recovery rows: `143`
- Boundary hotspot rows: `143`
- Missing observation rows: `0`
- Original actions: action `6` `79`，action `5` `41`，action `1` `23`
- Target actions: action `2` `102`，action `1` `17`，action `3` `16`，action `5` `7`，action `7` `1`
- Target labels: `geometry_inward_non_wallward_action` `126`，`highest_scored_non_wallward_action` `17`

## 判断

这批样本精准覆盖 history probe 发现的 `20s` 后 online action `6` 邻域，但 target action 明显偏向 action `2`，占 `0.7133`。因此它只能作为下一轮训练的一个小权重 repair input，不能直接高权重混入 opening 子模型；否则可能把 action `6` bias 转成 action `2` bias。

下一步训练建议：

- 保留 `class_weighting = none`
- 把这批 online route-risk samples 与原多图 boundary samples 合并，但使用低权重或单独消融
- 先跑 dry-run 检查 target action balance
- 训练后仍只跑 60 秒 high-pressure 三图 deterministic gate

## 输出文件

- `online_route_risk_samples.jsonl`
- `export_report.json`
- `export_report.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
