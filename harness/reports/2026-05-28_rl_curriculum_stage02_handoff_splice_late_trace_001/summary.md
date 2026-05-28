# Stage 02 Handoff Splice Late Trace Samples

## 结论

- Decision: `handoff_splice_late_trace_samples_recorded_not_policy_gate`
- Source policy: stage 02 SB3 opening for first `60s`, then handoff splice staged fallback
- Source probe: `harness/reports/2026-05-28_rl_curriculum_stage02_handoff_splice_wrapper_probe_001/summary.md`
- Trace comparison: `comparison_300s_trace.json`
- Hotspot report: `route_recovery_hotspots.md`
- Late sample validation: `late_route_recovery_samples_validation.md`

本报告复跑 handoff splice wrapper 的 `300s` high-pressure 三图失败局，并写入 sampled observation trace。目标是把 `fail_20260528_086` 暴露出的 late-window 失败面转成更窄的 repair training input，而不是训练或放行新的 policy。

结果与上一轮 handoff splice probe 一致：三张高压地图 300 秒仍为 `0.0/0.0/0.0`，gate 仍是 `multimap_comparison_recorded_needs_policy_repair`。本次 trace 只记录失败局，共 `9` 条失败 trace、`1686` 个 sampled rows，其中 negative `route_recovery` rows 为 `965`，占 `57.24%`。

## Trace Hotspots

| Item | Value |
| --- | ---: |
| Failed traces | `9` |
| Sampled rows | `1686` |
| Negative route_recovery rows | `965` |
| Negative route_recovery ratio | `57.24%` |
| Boundary-edge hotspots | `884` |
| Main pressure | `boundary_edge` |

Map hotspot counts:

| Map | Hotspots | Dominant hotspot actions |
| --- | ---: | --- |
| `soda-creek` | `282` | action `5`, `2`, `7` |
| `caramel-workshop` | `299` | action `5`, `2`, `3` |
| `cracked-star-jar` | `384` | action `5`, `3`, `2` |

Time bucket hotspot counts:

| Bucket | Hotspots | Dominant hotspot actions |
| --- | ---: | --- |
| `opening_lt_60` | `345` | action `2`, `7`, `4` |
| `mid_60_to_180` | `394` | action `5`, `3`, `8` |
| `late_180_to_300` | `226` | action `3`, `5`, `8` |

## Exported Late Repair Samples

| Slice | Samples | Validation |
| --- | ---: | --- |
| `180-300s all maps` | `207` | `edge_recovery_samples_valid` |

Late sample distribution:

| Map | Samples |
| --- | ---: |
| `soda-creek` | `43` |
| `caramel-workshop` | `61` |
| `cracked-star-jar` | `103` |

Original actions are concentrated in action `3` (`106`) and action `5` (`78`), while target actions are mostly action `1` (`129`) and action `5` (`44`). This reinforces that the splice is still boundary-pinned under late pressure, but the repair samples are not enough by themselves to prove a policy fix.

## 判断

- This trace narrows the next repair input to late-window boundary-edge route recovery instead of another broad splice.
- The `207` exported rows are valid behavior-clone repair material only; they are not Replay evidence, not a fixed policy, not a balance gate, and not RL acceptance.
- 下一步若继续 supervised fallback，应 mix this late slice at very low weight with current-failure best as a hard retention anchor, then rerun seed `63100` `60/180/300s` no-regression against current-failure best before any longer run.
- 如果再次丢掉 `cracked-star-jar` 300 秒胜利，应停止 supervised sample stacking，转向 closed-loop constrained repair 或 per-map late win-conversion objective。

## 输出文件

- `comparison_300s_trace.json`
- `traces/`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `late_route_recovery_samples.jsonl`
- `late_route_recovery_samples_report.json`
- `late_route_recovery_samples.md`
- `late_route_recovery_samples_validation.json`
- `late_route_recovery_samples_validation.md`
