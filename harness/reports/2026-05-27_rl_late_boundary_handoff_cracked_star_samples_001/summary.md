# Cracked Star Jar Handoff Recovery Samples

## 结论

- Decision: `cracked_star_handoff_samples_exported_not_policy_gate`
- Source traces: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_obs_samples_001/traces_180s_obs/`
- Samples: `cracked_star_handoff_60_90_recovery_samples.jsonl`
- Sample validation: `edge_recovery_samples_valid`
- Dry run gate: `dataset_validated_not_training_gate`

本轮使用 `tools/export_route_recovery_samples.py --map-id cracked-star-jar` 从现有 `stage01 opening wrapper + handoff_mid_w0_5 fallback` observation trace 中切出 `cracked-star-jar` 专项 handoff 样本。过滤条件与上一轮 60-90 秒样本一致：`60-90s`、负 `route_recovery`、`boundary.edge_risk >= 0.75`、`min_health_ratio = 0.25`，并用 `phase_duration_seconds = 300` 改写 observation progress。

导出结果是 `190` 条样本，全部来自 `cracked-star-jar`，覆盖 seed `62400-62404`，时间范围 `60.3328-89.999s`，`health_ratio` 平均 `0.5608`，没有低血量样本被过滤。`tools/validate_edge_recovery_samples.py` 判定样本结构与边界动作一致性通过；`train_behavior_clone.py --dry-run` 确认这批样本可作为 `gru context8`、map/time-phase conditioned 的 mid-window repair input。

## Sample Distribution

| Metric | Value |
| --- | ---: |
| Source traces | `15` |
| Map filtered traces | `10` |
| Inspected rows | `2182` |
| Negative route recovery rows | `218` |
| Boundary hotspot rows | `194` |
| Exported samples | `190` |

| Distribution | Counts |
| --- | --- |
| Map | `{"cracked-star-jar": 190}` |
| Original actions | `{"2": 88, "3": 86, "8": 16}` |
| Target actions | `{"7": 86, "6": 41, "1": 34, "3": 29}` |
| Target labels | `{"geometry_inward_non_wallward_action": 127, "highest_scored_non_wallward_action": 63}` |

这批专项样本和上一轮 failure analysis 之间有一个重要约束：300 秒 fallback-only 失败里 `cracked-star-jar` 的 action `7` 占比已经达到 `61.49%`，但本批样本的 target action `7` 也占 `45.26%`，因为它在部分右侧边界状态里是内向动作。因此下一步训练不能简单做全局 action `7` 惩罚或全局 action `7` 加权；必须保留 map conditioning、position diagnostics、soft target 和 action distribution regularization，让动作语义随边界位置变化。

## 下一步

- 可把这批 `190` 条样本作为 `cracked-star-jar` 专项 handoff repair input，与三图 phase-aligned KiteBot 轨迹混合做低权重 mid-only 或 fallback-specific 消融。
- 训练时必须继续跑 60/180/300 秒 high-pressure 三图；单图样本导出不是 RL acceptance，也不能解除 `rl_policy_multimap_generalization_gap`。
- 如果专项样本继续把 action `7` 扩散成跨图 dominant action，应转向 late-window low-health / hazard / Boss pressure recovery，而不是继续增加同类 handoff 样本。

## 输出文件

- `cracked_star_handoff_60_90_recovery_samples.jsonl`
- `sample_export.json`
- `sample_export.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
