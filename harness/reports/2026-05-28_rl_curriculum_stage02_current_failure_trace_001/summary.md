# Stage 02 Current-failure Trace Samples

## 结论

- Decision: `current_failure_trace_samples_recorded_not_policy_gate`
- Source policy: stage 02 opening for first `60s`, then current-failure fallback
- Source probe: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/summary.md`
- Trace comparison: `comparison_300s_trace.json`
- Hotspot report: `route_recovery_hotspots.md`
- Behavior clone dry-run: `behavior_clone_dry_run_samples.json`

本报告复跑 current-failure fallback 的 `300s` high-pressure 三图失败局 trace，并写入 policy observation。目标是定位当前最佳监督 fallback 分支剩余失败面，导出更细的 map/time-window repair inputs，而不是训练或放行新的 policy。

结果与上一轮 current-failure fallback probe 一致：`soda-creek` 与 `caramel-workshop` 300 秒胜率仍为 `0.0`，`cracked-star-jar` 为 `0.3333`。本次只写失败局 trace，共 `8` 条失败 trace，`1369` 个 sampled rows 中有 `926` 个 negative route_recovery rows，占 `67.64%`。

## Trace Hotspots

| Item | Value |
| --- | ---: |
| Failed traces | `8` |
| Sampled rows | `1369` |
| Negative route_recovery rows | `926` |
| Negative route_recovery ratio | `67.64%` |
| Boundary-edge hotspots | `885` |
| Main pressure | `boundary_edge` |

Map hotspot counts:

| Map | Hotspots | Dominant hotspot actions |
| --- | ---: | --- |
| `soda-creek` | `346` | action `1`, `3`, `2` |
| `caramel-workshop` | `341` | action `3`, `2`, `5` |
| `cracked-star-jar` | `239` | action `5`, `3`, `7` |

Time bucket hotspot counts:

| Bucket | Hotspots | Dominant hotspot actions |
| --- | ---: | --- |
| `opening_lt_60` | `306` | action `2`, `7`, `4` |
| `mid_60_to_180` | `475` | action `3`, `5`, `1` |
| `late_180_to_300` | `145` | action `3`, `5`, `1` |

## Exported Repair Samples

| Slice | Samples | Validation |
| --- | ---: | --- |
| `soda-creek <60s` | `104` | `edge_recovery_samples_valid` |
| `soda-creek 60-180s` | `163` | `edge_recovery_samples_valid` |
| `soda-creek 180-300s` | `50` | `edge_recovery_samples_valid` |
| `caramel-workshop <60s` | `102` | `edge_recovery_samples_valid` |
| `caramel-workshop 60-180s` | `163` | `edge_recovery_samples_valid` |
| `caramel-workshop 180-300s` | `45` | `edge_recovery_samples_valid` |
| `cracked-star-jar 60-180s` | `116` | `edge_recovery_samples_valid` |
| `cracked-star-jar 180-300s` | `29` | `edge_recovery_samples_valid` |

Combined behavior clone dry-run reads all `772` exported rows as `edge_recovery_supervision` and returns `dataset_validated_not_training_gate`. Soft target conversion covers all `772` rows with `top_k_scores`, `fallback_one_hot_count = 0`, and average nonzero actions `2.4067`.

## 判断

- Compared with the prior path-weighted trace, this branch has fewer sampled rows and a lower negative route_recovery ratio, matching the improved 300 秒 average survival from the current-failure fallback probe.
- The remaining samples still concentrate on boundary-edge route recovery, with a clearer mid-window load on `soda-creek` / `caramel-workshop` and a smaller late-window tail.
- Opening-window samples remain visible because the staged wrapper still uses the fixed stage 02 opening policy before `60s`; these samples are diagnostic material for future opening repair, not evidence that the fallback can fix pre-60s deaths.
- These rows are repair training material only. They are not Replay evidence, not a fixed policy, not a balance gate, and not RL acceptance evidence.
- 下一轮若继续 supervised fallback，应 use this trace as the narrower current-failure sample pack, then rerun seed 63100 `60/180/300s` no-regression before considering any further stage movement.

## 输出文件

- `comparison_300s_trace.json`
- `traces/`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `soda_opening_route_recovery_samples.jsonl`
- `soda_opening_route_recovery_samples_report.json`
- `soda_opening_route_recovery_samples_validation.json`
- `soda_mid_route_recovery_samples.jsonl`
- `soda_mid_route_recovery_samples_report.json`
- `soda_mid_route_recovery_samples_validation.json`
- `soda_late_route_recovery_samples.jsonl`
- `soda_late_route_recovery_samples_report.json`
- `soda_late_route_recovery_samples_validation.json`
- `caramel_opening_route_recovery_samples.jsonl`
- `caramel_opening_route_recovery_samples_report.json`
- `caramel_opening_route_recovery_samples_validation.json`
- `caramel_mid_route_recovery_samples.jsonl`
- `caramel_mid_route_recovery_samples_report.json`
- `caramel_mid_route_recovery_samples_validation.json`
- `caramel_late_route_recovery_samples.jsonl`
- `caramel_late_route_recovery_samples_report.json`
- `caramel_late_route_recovery_samples_validation.json`
- `cracked_mid_route_recovery_samples.jsonl`
- `cracked_mid_route_recovery_samples_report.json`
- `cracked_mid_route_recovery_samples_validation.json`
- `cracked_late_route_recovery_samples.jsonl`
- `cracked_late_route_recovery_samples_report.json`
- `cracked_late_route_recovery_samples_validation.json`
- `behavior_clone_dry_run_samples.json`
