# Late Pressure Recovery Sample Slices

## 结论

- Gate decision: `late_pressure_recovery_samples_recorded_not_training_gate`
- Source traces: `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/traces_300s_obs`
- Hotspot report: `route_recovery_hotspots.md`
- Behavior clone dry-run: `behavior_clone_dry_run.json`

本轮为下一步 late-window repair 做数据切片，不训练模型、不推进 stage 03、不作为 RL acceptance。基于 9 条 300 秒 observation trace，`analyze_route_recovery_traces.py` 记录 966 个采样行，其中 735 个为负 route_recovery；180-300 秒窗口只有 42 个 late boundary hotspot。

## Samples

| Slice | Decision | Samples | Maps | Original actions | Target actions |
| --- | --- | ---: | --- | --- | --- |
| `late_low_health` | `route_recovery_samples_exported` | `7` | `cracked-star-jar` | `4` | `8` |
| `late_hazard` | `route_recovery_samples_unavailable` | `0` | none | none | none |
| `late_boss` | `route_recovery_samples_exported` | `1` | `soda-creek` | `4` | `8` |

`late_low_health` 和 `late_boss` 都通过 `validate_edge_recovery_samples.py`；`late_hazard` 在 180-300 秒窗口没有可导出的 boundary-pinned negative route_recovery 样本，因此保留 unavailable 结果而不伪造训练输入。

## Dry Run

将 7 条 low-health 样本和 1 条 boss-pressure 样本合并输入 `train_behavior_clone.py --dry-run` 后，训练入口返回 `dataset_validated_not_training_gate`，识别到 `8` 条 edge recovery rows，时间窗过滤保留 `8/8`。样本全部指向 target action `8`，规模过小且动作单一，只能作为诊断或后续采样策略输入。

## 判断

- 当前 trace 里的 late pressure 可用样本太少，直接训练很可能造成 action `8` 过拟合。
- hazard pressure 在 late 窗口没有样本，下一步应优先采集覆盖 hazard/Boss/low-health 的 180-300 秒 observation traces，而不是继续对这 8 条样本调权重。
- 新增导出过滤参数可用于后续更大 trace 集：`--max-health-ratio`、`--min-low-health-risk`、`--min-hazard-pressure-risk`、`--min-boss-pressure-risk`。

## 输出文件

- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `late_low_health_recovery_samples.jsonl`
- `late_low_health_export.json`
- `late_low_health_export.md`
- `late_low_health_validation.json`
- `late_low_health_validation.md`
- `late_hazard_recovery_samples.jsonl`
- `late_hazard_export.json`
- `late_hazard_export.md`
- `late_hazard_validation.json`
- `late_hazard_validation.md`
- `late_boss_recovery_samples.jsonl`
- `late_boss_export.json`
- `late_boss_export.md`
- `late_boss_validation.json`
- `late_boss_validation.md`
- `behavior_clone_dry_run.json`
