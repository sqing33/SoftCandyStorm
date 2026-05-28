# Stage 02 Path-weighted Fallback Trace Samples

## 结论

- Decision: `path_weighted_trace_samples_recorded_not_policy_gate`
- Source policy: stage 02 opening for first `60s`, then path-weighted fallback
- Source probe: `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_fallback_probe_001/summary.md`
- Trace comparison: `comparison_300s_trace.json`
- Hotspot report: `route_recovery_hotspots.md`
- Behavior clone dry-run: `behavior_clone_dry_run_samples.json`

本报告复跑上一轮 path-weighted fallback 的 `300s` high-pressure 三图失败局 trace，并写入 policy observation。目标是把当前失败面切成更细的 map/time-window repair inputs，而不是训练或放行新的 policy。

结果与上一轮 300 秒对比一致：`soda-creek` 与 `caramel-workshop` 300 秒胜率仍为 `0.0`，`cracked-star-jar` 保持 `0.3333`。本次只写失败局 trace，共 `8` 条失败 trace，`2359` 个 sampled rows 中有 `1724` 个 negative route_recovery rows，占 `73.08%`。

## Trace Hotspots

| Item | Value |
| --- | ---: |
| Failed traces | `8` |
| Sampled rows | `2359` |
| Negative route_recovery rows | `1724` |
| Negative route_recovery ratio | `73.08%` |
| Main pressure | `boundary_edge` |

Map hotspot counts:

| Map | Hotspots | Dominant hotspot actions |
| --- | ---: | --- |
| `soda-creek` | `524` | action `8`, `2`, `7` |
| `caramel-workshop` | `783` | action `3`, `2`, `7` |
| `cracked-star-jar` | `417` | action `8`, `2`, `7` |

Time bucket hotspot counts:

| Bucket | Hotspots | Dominant hotspot actions |
| --- | ---: | --- |
| `opening_lt_60` | `606` | action `2`, `7`, `4` |
| `mid_60_to_180` | `865` | action `3`, `8`, `5` |
| `late_180_to_300` | `253` | action `3`, `8`, `5` |

## Exported Repair Samples

| Slice | Samples | Validation |
| --- | ---: | --- |
| `soda-creek 60-180s` | `227` | `edge_recovery_samples_valid` |
| `soda-creek 180-300s` | `50` | `edge_recovery_samples_valid` |
| `cracked-star-jar 60-180s` | `202` | `edge_recovery_samples_valid` |
| `caramel-workshop <60s` | `202` | `edge_recovery_samples_valid` |
| `caramel-workshop 180-300s` | `144` | `edge_recovery_samples_valid` |

Combined behavior clone dry-run reads all `825` exported rows as `edge_recovery_supervision` and returns `dataset_validated_not_training_gate`. Soft target conversion covers all `825` rows with `top_k_scores`, `fallback_one_hot_count = 0`, and average nonzero actions `2.4376`.

## 判断

- 当前 path-weighted fallback 的失败面仍主要是 boundary-edge route recovery，而不是数据入口不可用。
- Compared with the prior late-retention map repair samples, this current-failure trace has a wider export surface: `825` rows across soda mid/late, cracked mid, and caramel opening/late.
- These rows are repair training material only. They are not Replay evidence, not a fixed policy, not a balance gate, and not RL acceptance evidence.
- 下一轮若继续 supervised fallback，应优先做更窄的 path weights 或 map/time-window curriculum，并继续使用 seed 63100 `60/180/300s` no-regression gate。

## 输出文件

- `comparison_300s_trace.json`
- `traces/`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `soda_mid_route_recovery_samples.jsonl`
- `soda_mid_route_recovery_samples_report.json`
- `soda_mid_route_recovery_samples_validation.json`
- `soda_late_route_recovery_samples.jsonl`
- `soda_late_route_recovery_samples_report.json`
- `soda_late_route_recovery_samples_validation.json`
- `cracked_mid_route_recovery_samples.jsonl`
- `cracked_mid_route_recovery_samples_report.json`
- `cracked_mid_route_recovery_samples_validation.json`
- `caramel_opening_route_recovery_samples.jsonl`
- `caramel_opening_route_recovery_samples_report.json`
- `caramel_opening_route_recovery_samples_validation.json`
- `caramel_late_route_recovery_samples.jsonl`
- `caramel_late_route_recovery_samples_report.json`
- `caramel_late_route_recovery_samples_validation.json`
- `behavior_clone_dry_run_samples.json`
