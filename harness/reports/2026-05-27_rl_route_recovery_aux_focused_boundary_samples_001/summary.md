# Route Recovery Aux Focused Boundary Samples

## 结论

- Gate decision: `dataset_validated_not_training_gate`
- 来源：`route_recovery_aux_entropy_retry` checkpoint 的 `soda-creek` seed `62300` 60 秒 sampled trace
- 样本数：`134`
- 角色：`edge_recovery_supervision_sample` / `repair_training_input`
- 校验：`tools/validate_edge_recovery_samples.py` 返回 `edge_recovery_samples_valid`

这批样本把 history context probe 暴露出的在线右边界卡住问题，转成几何安全的边界恢复训练材料。导出过程没有直接复制 nearest teacher action；因为 teacher action 在不同位置下可能不是当前在线状态的安全动作。导出器只保留当前在线 trace 中满足以下条件的帧：

- `route_recovery < 0`
- `boundary.edge_risk >= 0.75`
- 原始 action 继续顶入地图边界
- 目标 action 不再顶入记录中的边界

## 分布

- 原始动作：action `3` 共 `82` 条，action `5` 共 `52` 条。
- 目标动作：action `7` 共 `63` 条，action `8` 共 `42` 条，action `5` 共 `22` 条，action `1` 共 `7` 条。
- 目标选择：`geometry_inward_non_wallward_action` 共 `95` 条，`highest_scored_non_wallward_action` 共 `39` 条。
- 时间范围：`6.6667-60.0328s`
- 地图 / seed：`soda-creek` seed `62300`

## 限制

这批样本只证明 focused repair input 可以被导出、校验和行为克隆 dry-run 读取。它不是 policy checkpoint，不是 Replay，不是 deterministic high-pressure gate，也不是 RL acceptance 证据。

后续如果用它训练修复候选，必须重新跑至少：

- behavior clone 训练报告
- deterministic high-pressure 60 / 180 / 300 秒多图对比
- failure case 复核
- RL policy acceptance manifest

## 输出文件

- `focused_boundary_samples.jsonl`
- `export_report.json`
- `sample_validation.json`
- `behavior_clone_dry_run.json`
