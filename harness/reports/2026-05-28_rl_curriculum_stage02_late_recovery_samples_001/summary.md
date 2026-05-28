# Stage 02 Late Route Recovery Samples

## 结论

- Decision: `route_recovery_samples_exported`
- Source traces: `harness/reports/2026-05-28_rl_curriculum_stage02_late_trace_hotspots_001/traces/`
- Time window: `180-300s`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_late_recovery_samples_001/late_route_recovery_samples.jsonl`
- Validation: `edge_recovery_samples_valid`
- Behavior clone dry-run: `dataset_validated_not_training_gate`

本报告从 stage 02 失败 trace 中导出 late-window route-recovery repair samples。样本只来自 180-300 秒窗口内的 boundary-pinned negative `route_recovery` 热点，可作为后续 behavior clone / policy repair 输入；它不是 RL policy acceptance、不是 playtest 证据，也不代表 stage 02 checkpoint 可推进。

## Export Summary

| Metric | Value |
| --- | ---: |
| Source traces | `8` |
| Inspected trace rows | `3553` |
| Negative route_recovery rows in window | `551` |
| Boundary hotspot rows | `533` |
| Exported samples | `527` |
| Missing observation rows | `0` |

## Distributions

| Dimension | Distribution |
| --- | --- |
| Maps | `{"caramel-workshop": 195, "cracked-star-jar": 132, "soda-creek": 200}` |
| Original actions | `{"2": 217, "3": 27, "4": 158, "7": 125}` |
| Target actions | `{"0": 20, "1": 5, "3": 119, "4": 26, "5": 23, "6": 186, "7": 30, "8": 118}` |
| Target labels | `{"geometry_inward_non_wallward_action": 439, "highest_scored_non_wallward_action": 88}` |

## Validation

- `tools/validate_edge_recovery_samples.py` reported `edge_recovery_samples_valid` with `0` errors and `0` warnings.
- `train_behavior_clone.py --dry-run` loaded all `527` samples as `edge_recovery_sample_records`.
- Dry-run phase distribution is `late = 1.0`, `opening = 0.0`, `mid = 0.0`.
- This validates training-input shape only; any actual policy must still pass deterministic 60 / 180 / 300 second high-pressure comparisons.

## Next

下一步实验应基于这些样本训练一个严格限定范围的 late repair model，再用同一组固定 60 / 180 / 300 秒窗口和 stage 02 PPO checkpoint 对比。如果短窗回归，或 300 秒仍有 0 胜率地图，应记录新的 failure case，而不是推进候选。
