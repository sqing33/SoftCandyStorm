# Route Recovery Trace Hotspots

## 结论

`route_recovery` trace 热点分析已把上一轮 300 秒 high-pressure 失败面收窄到“贴边后仍持续选择边界方向动作”的路线恢复问题。该报告只分析 sampled trace 行，不是 Replay，也不是 RL policy acceptance 证据；结论仍为 `repair`。

- Source: `harness/reports/2026-05-27_rl_route_recovery_reward_profile_smoke_001/traces_300s/`
- Tool: `tools/analyze_route_recovery_traces.py`
- Traces: `9`
- Sampled rows: `966`
- Negative `route_recovery` rows: `735` / `76.09%`
- Full hotspot report: `route_recovery_hotspots.md`

## Key Findings

| Dimension | Finding |
|---|---|
| Dominant pressure | `boundary_edge` appears in `721` negative samples |
| Dominant action | action `4` appears in `401` boundary-edge hotspot rows |
| Worst map | `cracked-star-jar` has the lowest sampled `route_recovery = -0.0088` |
| Worst window | `mid_60_to_180` has `358` negative samples and contains the worst row |
| Late severity | `late_180_to_300` has fewer rows but worse average `route_recovery = -0.0066` |

The top 20 worst rows all come from `cracked-star-jar` seed `62300`, mostly between `166s` and `185s`, with `boundary.min_distance = 0` and action `4` remaining the model's top action. This means the immediate repair target is not generic reward scaling; it is a boundary-pinned action selection failure.

## Next

Do not directly increase `route_recovery` weight. The next repair should convert the boundary-pinned hotspot rows into a supervised recovery or policy-constraint experiment, especially for mid and late windows, and then rerun high-pressure 60 / 180 / 300 second gates. Until then, `rl_policy_multimap_generalization_gap` remains open.
