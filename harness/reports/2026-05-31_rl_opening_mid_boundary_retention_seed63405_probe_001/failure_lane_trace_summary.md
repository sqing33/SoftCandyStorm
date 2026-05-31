# RL Failure Lane Trace Summary

- Decision: `rl_failure_lane_trace_diagnostics_recorded`
- Source plan: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_lane_trace_plan.json`
- Source failure analysis: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_analysis_caramel_300s_10seed.json`
- Map: `caramel-workshop`
- Gate conclusion: `repair`

## Lane Results

| Lane | Seeds | Traces | Sampled Rows | Negative route_recovery | Main Pressure | Main Actions | Diagnosis |
|---|---:|---:|---:|---:|---|---|---|
| `opening_repair` | `63402` | 1 | 82 | 51 (62.20%) | `boundary_edge` | `5`, `4`, `2` | 0-60 秒 opening boundary/action-lock 问题 |
| `late_terminal_survival_conversion` | `63400`, `63401`, `63403`, `63404`, `63405`, `63406`, `63408`, `63409` | 8 | 3479 | 2599 (74.71%) | `boundary_edge` | `5`, `7`, `1`, `3` | late death 前已有 opening/mid route debt |

## Opening Repair

`opening_repair` 只包含 seed `63402`。本次 trace 中 1 局仍在 `40.0997s` defeat，candidate action distribution 的 dominant action 是 `5`，ratio 为 `0.6891`。route hotspot 采样到 `82` 行，其中 `51` 行为负 `route_recovery`，全部落在 `opening_lt_60`；压力主要是 `boundary_edge`，共 `47` 个热点，动作集中在 action `5` 和 action `4`。

结论：seed `63402` 应继续作为独立 opening branch / target preflight lane 处理，不能并入 late terminal conversion 或 shared PPO continuation。

## Late Terminal Survival Conversion

`late_terminal_survival_conversion` 的 late-only 分析过滤出 8 条真实 late failure seed，排除连续扫描额外带入的 seed `63402` 和 `63407`。8 条 trace 共 `3479` 个 sampled rows，其中 `2599` 行为负 `route_recovery`，ratio 为 `74.71%`。

按时间桶看，负热点并不只在 late：`opening_lt_60` 有 `573` 个，`mid_60_to_180` 有 `1505` 个，`late_180_to_300` 有 `521` 个。按压力看，`boundary_edge` 占 `2482` 个热点，远高于 `hazard_pressure` 的 `297` 和 `low_health` 的 `106`。这说明 180-300 秒死亡不是纯 late-only low-health 动作选择问题，terminal conversion 前已经积累了 opening/mid route debt。

## Next Gates

- `opening_repair`：先做 seed `63402` 的窄 state-conditioned branch 或 target preflight，再跑 60s/caramel hard preflight 和 high-pressure parent no-regression。
- `late_terminal_survival_conversion`：同时保护 `60-180s` path retention 与 `180-300s` terminal conversion，不直接把问题交给纯 late low-health 或 terminal branch。
- 任一 lane 的下一步都必须继续保留 10 seed caramel follow-up、60s/caramel hard preflight、high-pressure 60/180/300s parent no-regression。

## Limitations

- 本报告只分析 sampled trace rows，不替代 Replay 或完整 GameCore snapshot regression。
- late trace 命令为了连续 seed range 扫到了 seed `63402` 和 `63407`，late-only 结论必须使用过滤后的 `route_hotspots_late_seeds_only`。
- 负 `route_recovery` 热点是 repair routing evidence，不是 policy acceptance、RL test Bot 或 stage 03 许可。
