# Stage 02 Late Trace Hotspots

## 结论

`stage_02_late_180_to_300` 的 300 秒 high-pressure failed-only trace 已确认：终局失败全部落在 `late_180_to_300`，但负 `route_recovery` 热点从 opening / mid 就开始积累，主要压力仍是贴边路线恢复失败。该报告只分析 sampled trace 行，不是 Replay，也不是 RL policy acceptance 证据；结论仍为 `repair`。

- Source model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Comparison: `comparison_300s_failed_trace.json`
- Trace dir: `traces/`
- Tool: `tools/analyze_route_recovery_traces.py`
- Traces: `8`
- Sampled rows: `3553`
- Negative `route_recovery` rows: `2820` / `79.37%`
- Full hotspot report: `route_recovery_hotspots.md`

## Key Findings

| Dimension | Finding |
| --- | --- |
| Dominant pressure | `boundary_edge` appears in `2744` negative samples |
| Worst map by count | `caramel-workshop` has `1147` hotspots, dominated by action `2` (`706` rows) |
| Soda pattern | `soda-creek` has `1019` hotspots split across action `2` (`413`), action `7` (`377`) and action `4` (`222`) |
| Cracked pattern | `cracked-star-jar` has `654` hotspots, with action `7` (`269`) and action `4` (`198`) leading |
| Time spread | `mid_60_to_180` has `1569` hotspots; `late_180_to_300` has `551`, so terminal late failures have earlier route debt |
| Low health risk | `low_health` appears in `195` negative samples and is mostly action `7` (`110`) |

The worst sampled rows are boundary-edge frames with `route_recovery = -0.0025`. The important shift from stage 01 is not that the policy suddenly becomes healthy in early windows; rather, it survives those windows while accumulating route-recovery debt that later becomes unrecoverable on `soda-creek` and `caramel-workshop`.

## Next

Do not promote this checkpoint or start a stage 03 acceptance run. The next repair input should export route-recovery supervision samples from these failed traces, with separate attention to `caramel-workshop` action `2` and `soda-creek` / `cracked-star-jar` action `7` boundary-edge failures, then rerun the fixed 60 / 180 / 300 second comparisons.
