# Stage 02 Late-retention Map Repair Samples

## 结论

- Gate decision: `late_retention_map_repair_samples_exported_not_acceptance`
- Source policy: stage 02 opening for first `60s`, then late-retention fallback
- Source comparison: `comparison_300s_trace.json`
- Hotspot report: `route_recovery_hotspots.md`

本报告复跑当前 late-retention fallback best branch 的 `300s` high-pressure 三图失败局 trace，并只为失败局写入带 observation 的 sampled trace。目标是从当前失败面导出下一轮 map-specific supervised repair training input，而不是复用上一版 fallback 的旧失败样本。

结果与上一轮 late-retention probe 一致：`soda-creek` 与 `caramel-workshop` 300 秒胜率仍为 `0.0`，`cracked-star-jar` 300 秒保持 `0.3333`。这不是新 policy，也不是 RL acceptance evidence。

## Trace Hotspots

- Failed traces: `8`
- Sampled rows: `1202`
- Negative route_recovery rows: `861` (`71.63%`)
- Dominant pressure tag: `boundary_edge`，共 `830` 行

| Bucket | Hotspots | Dominant Actions |
| --- | ---: | --- |
| `opening_lt_60` | `306` | `2`, `7`, `4` |
| `mid_60_to_180` | `446` | `3`, `8`, `5` |
| `late_180_to_300` | `109` | `3`, `8`, `5` |

## Exported Repair Samples

| Window | Map | Samples | Main Original Actions | Validation |
| --- | --- | ---: | --- | --- |
| `60-180s` | `soda-creek` | `115` | `8`, `3`, `5` | `edge_recovery_samples_valid` |
| `<60s` | `caramel-workshop` | `102` | `2`, `7` | `edge_recovery_samples_valid` |
| `180-300s` | `caramel-workshop` | `46` | `3`, `5`, `8` | `edge_recovery_samples_valid` |

## 判断

- 当前失败面比上一轮 staged fallback trace 窄：sampled rows 从 `3745` 降到 `1202`，但 route recovery 负样本比例仍高达 `71.63%`。
- 下一轮训练应低权重混入这三包 map-specific samples，并继续保留真实 late-survival trajectories，避免再次破坏 `cracked-star-jar` 300 秒胜率。
- 这些样本只能作为 repair training input，不能作为 policy gate、stage 03 或 RL acceptance 证据。

## 输出文件

- `comparison_300s_trace.json`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `soda_mid_route_recovery_samples.jsonl`
- `soda_mid_route_recovery_samples.json`
- `soda_mid_route_recovery_samples.md`
- `soda_mid_route_recovery_samples_validation.json`
- `soda_mid_route_recovery_samples_validation.md`
- `caramel_opening_route_recovery_samples.jsonl`
- `caramel_opening_route_recovery_samples.json`
- `caramel_opening_route_recovery_samples.md`
- `caramel_opening_route_recovery_samples_validation.json`
- `caramel_opening_route_recovery_samples_validation.md`
- `caramel_late_route_recovery_samples.jsonl`
- `caramel_late_route_recovery_samples.json`
- `caramel_late_route_recovery_samples.md`
- `caramel_late_route_recovery_samples_validation.json`
- `caramel_late_route_recovery_samples_validation.md`
- `traces/*_trace.json`
