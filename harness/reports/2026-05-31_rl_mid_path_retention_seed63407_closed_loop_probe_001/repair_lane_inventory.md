# RL Repair Lane Inventory

- Decision: `rl_repair_lane_inventory_recorded`
- Source split plan: `repair_split_plan.json`
- Source hard gate: `repair_probe_gate_hard_preflight.json`
- Lanes: `5`

## Lane Summary

| Lane | Split status | Reuse decision | Next action |
|---|---|---|---|
| `target63407` | `passed` | `keep_as_required_evidence` | 保留为下一轮 hard gate 的 required evidence，但不能覆盖其他失败 lane。 |
| `opening63402` | `failed` | `reuse_narrow_opening_branch_as_diagnostic_only` | 单独走 opening repair，复用 narrow state-conditioned branch 作为诊断证据，再跑 target preflight 与 parent no-regression。 |
| `retention63405` | `failed` | `trace_diagnostic_recorded_boundary_path_retention_lane` | 按 opening + mid-window boundary/path retention lane 设计修复；不得继续把 `63405` 混入 `63407` shared PPO continuation。 |
| `short60` | `failed` | `keep_as_hard_preflight` | 未来任何 `63407` 或 `63405` continuation 都必须先过 `60s/caramel-workshop` early-stop preflight。 |
| `parent` | `failed` | `keep_as_required_no_regression` | 继续作为所有 follow-up 的 required no-regression lane；target seed 改善也不能越过 parent 回归。 |

## Existing Evidence

### `target63407`

- `target_seed_preflight_seed63407.json`: seed `63407` 在当前 closed-loop probe 中达到 `300.0150s` victory。
- `repair_split_plan.json`: 该 lane 是 split plan 中唯一通过的 lane。

### `opening63402`

- `target_seed_preflight_seed63402_opening.json`: 当前 `mid-path-retention` checkpoint 仍让 `caramel-workshop:63402` 在 `40.0997s` defeat。
- `harness/reports/2026-05-30_rl_caramel_opening_edge_branch_probe_001/summary.md`: narrow `30-45s` caramel opening branch 通过 target seed preflight 与 parent no-regression，但仍是 evaluation-only。
- `harness/reports/2026-05-31_rl_terminal_sequence_selective_opening_guard_followup_001/summary.md`: selective opening guard 把 seed `63402` 推到 `300.0150s`，但牺牲 seed `63407` 并让 10 seed follow-up 失败。

### `retention63405`

- `target_seed_preflight_seed63405_retention.json`: 当前 checkpoint 让 `caramel-workshop:63405` 在 `138.6673s` defeat，未过 `180s` retention preflight。
- `harness/reports/2026-05-31_rl_terminal_sequence_selective_opening_guard_followup_001/summary.md`: 早先 selective opening guard follow-up 也让 seed `63405` 相对 baseline 回退 `23.9718s`，说明它不在 `63407` guard 证据覆盖内。
- `trace_compare_seed63405_parent_vs_candidate.json`: parent-vs-candidate trace compare 显示 candidate 比 parent 早死 `75.8496s`，首次动作分歧发生在 `13.0001s`（parent action `3` -> candidate action `7`），首次 high-pressure 从 parent 的 `100.9988s` 提前到 candidate 的 `45.9996s`。
- `route_hotspots_seed63405_parent_vs_candidate.json`: `248` 条负 route_recovery 采样中，热点集中在 `opening_lt_60` 和 `mid_60_to_180` 的 `boundary_edge` 压力；这不是纯 late low-health 问题。

### `short60`

- `window_target_preflight_60s_caramel.json`: 当前 `60s/caramel-workshop` 预检失败，win rate `0.3333`，average survival `49.2774s`。
- `harness/reports/2026-05-30_rl_caramel_opening_edge_branch_probe_001/summary.md`: narrow opening branch 曾把 `60s/caramel-workshop` 胜率做到 `1.0`，说明短窗需要独立保护。

### `parent`

- `window_regression_high_pressure_vs_parent.json`: 当前 checkpoint 触发 `60s/caramel-workshop` 胜率回归，以及 `180s/cracked-star-jar` / `300s/caramel-workshop` action-distribution L1 blockers。
- `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_branch_high_pressure_001/summary.md`: soda seed `63402` edge branch 可在不放宽 gate 的情况下通过 `60/180/300s` parent no-regression。
- `harness/reports/2026-05-30_rl_caramel_opening_edge_branch_probe_001/summary.md`: caramel narrow opening branch 也通过 parent no-regression，但没有解决 `300s` late conversion。

## Limitations

- 本盘点只复用已有报告，不重新仿真。
- evaluation-only wrapper 仍然只是诊断证据，不能直接成为 policy candidate。
- 后续若组合多个 lane，必须重新一起跑 target preflight、fixed-window no-regression 与 failure-case review。
