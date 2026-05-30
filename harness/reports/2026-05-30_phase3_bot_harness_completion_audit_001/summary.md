# Phase 3 Bot Harness Completion Audit

## 结论

- Decision: `phase3_bot_harness_complete`
- Scope: `docs/12 Phase 3 规则 Bot 与 Harness`
- Checked at: `2026-05-30`

本报告只审计 Phase 3：规则 Bot 与 Harness 基础设施。它不把 Bot gate 当作游戏好玩、内容正式接受、Runtime polish、RL acceptance、Release Candidate 或发布包通过证据。

## 验收项

| Requirement | Status | Evidence |
| --- | --- | --- |
| 9 个规则 Bot 已存在并可由 Harness 调用 | `pass` | `crates/bot_policies/src/lib.rs`, `crates/game_harness/src/main.rs` |
| 一条命令可以跑多 Bot 多 seed | `pass` | `harness/reports/2026-05-27_base_demo_bot_policy_calibration_600s_seed53000_20seed_001/summary.md`, `harness/reports/2026-05-27_base_demo_bot_policy_calibration_600s_seed52000_20seed_001/summary.md` |
| 输出 `summary.md` 和 `metrics.json` | `pass` | `harness/reports/2026-05-27_base_demo_bot_policy_calibration_600s_seed53000_20seed_001/summary.md`, `metrics.json` |
| 能拒绝明显坏信号 | `pass` | `harness/reports/2026-05-27_base_demo_all_bot_matrix_600s_seed53000_20seed_001/summary.md`, `harness/failed_cases/fail_20260527_006_base_demo_600s_bot_gate_regression.json` |
| 可配套 Replay 回归和 headless 性能预算 | `pass` | `harness/reports/2026-05-27_base_demo_bot_policy_calibration_600s_seed53000_20seed_replay_regression_001/summary.md`, `harness/reports/2026-05-27_harness_performance_budget_base_demo_calibration_seed53000_20seed_001/summary.md` |

## 判断

- Phase 3 的基础设施验收已满足：规则 Bot 阵列、批量矩阵、summary / metrics、坏信号拒绝、Replay 与性能预算侧证均有现存证据。
- 后续新增内容或调平衡时仍必须重新跑对应矩阵，不能复用本报告替代新内容门禁。
- 人工试玩、素材审查、剧情审校、Runtime 可读性、RL policy 和发布门禁继续独立阻塞。
