# Stage 02 Staged Opening Fallback Trace

## 结论

- Gate decision: `staged_opening_fallback_trace_recorded_not_acceptance`
- Policy: stage 02 opening for first `60s`, then soda/cracked retention fallback
- Source comparison: `comparison_300s_trace.json`
- Failure case: `harness/failed_cases/fail_20260528_071_stage02_soda_cracked_staged_opening_longrun_gap.json`

本报告复跑 stage 02 opening + soda/cracked retention fallback staged wrapper，在 `seed_start 63100`、`3` seed、high-pressure 三图、`300s` 窗口下只为失败局写入带 observation 的 sampled trace。目标是定位 fallback 在 `60-180` 与 `180-300` 的 route recovery 热点，并导出后续 repair training input。

结果与上一轮 staged opening probe 一致：`soda-creek` / `caramel-workshop` 300 秒胜率仍为 `0.0`，`cracked-star-jar` 为 `0.3333`。这不是新 policy，也不是 RL acceptance evidence。

## Trace Hotspots

- Failed traces: `8`
- Sampled rows: `3745`
- Negative route_recovery rows: `2856` (`76.26%`)
- Dominant pressure tag: `boundary_edge`，共 `2788` 行

| Bucket | Hotspots | Dominant Actions |
| --- | ---: | --- |
| `opening_lt_60` | `910` | `2`, `7`, `4` |
| `mid_60_to_180` | `1542` | `4`, `2`, `7` |
| `late_180_to_300` | `404` | `2`, `4`, `3` |

## Exported Repair Samples

| Window | Samples | Maps | Main Original Actions | Validation |
| --- | ---: | --- | --- | --- |
| `60-180s` | `1473` | caramel `580`, cracked `487`, soda `406` | `4`, `2`, `7` | `edge_recovery_samples_valid` |
| `180-300s` | `395` | cracked `176`, caramel `156`, soda `63` | `2`, `4`, `3` | `edge_recovery_samples_valid` |

## 判断

- Staged opening 保护了同 seed no-regression，但 fallback 仍把大量 sampled rows 推向边界，尤其是中窗 `60-180s`。
- 下一步如果训练，应先做低权重 fallback repair 消融，并继续使用 seed-matched stage 02 baseline 的 `60/180/300` no-regression gate。
- 这些样本只能作为 repair training input，不能作为 policy gate、stage 03 或 RL acceptance 证据。

## 输出文件

- `comparison_300s_trace.json`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `mid_route_recovery_samples.jsonl`
- `mid_route_recovery_samples.json`
- `mid_route_recovery_samples.md`
- `mid_route_recovery_samples_validation.json`
- `late_route_recovery_samples.jsonl`
- `late_route_recovery_samples.json`
- `late_route_recovery_samples.md`
- `late_route_recovery_samples_validation.json`
- `traces/*_trace.json`
