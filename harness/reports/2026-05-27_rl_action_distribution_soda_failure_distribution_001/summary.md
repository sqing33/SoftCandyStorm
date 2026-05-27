# Soda Failure Distribution Diagnostic

## 结论

- Gate decision: `diagnostic_recorded_not_policy_gate`
- Source evaluation: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/soda_180s_trace_eval.json`
- Source traces: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/traces`
- Related failure: `fail_20260527_048`

本轮解释了为什么扩展 `60-100s` midwindow samples 后，mid-only 消融仍没有修复 `soda-creek`：20 seed 的 180 秒评估里有 18 局失败，其中 14 局在 60 秒前死亡，只有 4 局进入 `60-180s` 中窗。也就是说，上一轮的 mid-only 训练主要修的是少数能活过 opening 的失败局，而主失败面仍然是 opening 早死。

## Failure Buckets

| Bucket | Failures | Ratio |
| --- | ---: | ---: |
| `opening_lt_60` | `14` | `77.78%` |
| `mid_60_to_180` | `4` | `22.22%` |
| `late_180_to_300` | `0` | `0.00%` |

整体 policy win rate 为 `0.1`，平均失败存活为 `49.3054s`。Opening 失败局通常由 action `3` dominant 触发；多个 seed 的 action `3` 占比为 `1.0`。

## Route Recovery Hotspots

| Bucket | Hotspots | Avg route_recovery | Actions |
| --- | ---: | ---: | --- |
| `opening_lt_60` | `1473` | `-0.0016` | `{"3": 1270, "6": 120, "1": 53, "5": 22, "2": 5, "7": 2, "4": 1}` |
| `mid_60_to_180` | `583` | `-0.0021` | `{"1": 489, "2": 86, "6": 8}` |

Pressure summary 也显示主要热点是 `boundary_edge`：`1960` 条；其中 action `3` 有 `1212` 条。最差热点集中在 opening 贴边、敌压或低血量状态，top action 仍高置信偏向 `3`。

## 判断

- `60-100s` mid samples 是有效训练输入，但不是当前最大 blocker。
- 直接提高 mid recovery weight 会把少数中窗边界样本放大，反而让其它地图 mid 行为偏向 action `5`。
- 下一步应回到 opening 失败面，但不能简单重训 opening；上一轮已证明粗暴 opening 重训会破坏多图短窗。
- 更合理的下一步是导出 `20-45s` 多 seed action `3` opening edge-risk samples，并只做低权重、per-map 受控、带 60 秒三图 hard gate 的 opening retention 消融。

## 输出文件

- `policy_failure_analysis.json`
- `policy_failure_analysis.md`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
