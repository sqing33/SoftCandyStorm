# SB3 E30 Map Late Split 180s Diagnostic

## 结论

- Decision: `sb3_e30_map_late_split_180s_probe_rejected_no_conversion`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Late branch: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/ppo_e30_opening_mid_retention_late_probe.zip`
- Split: `cracked-star-jar` after `180s`
- Probe type: evaluation-only split policy diagnostic, not a trained checkpoint
- Window regression vs e30: `policy_window_regression_passed`
- Window regression vs mid-anchor parent: `policy_window_regression_passed`
- Repair probe gate: `rl_repair_probe_gate_passed_for_limited_followup`
- Failure case: `harness/failed_cases/fail_20260529_006_sb3_e30_map_late_split_180s_probe_no_conversion.json`

该诊断把上一轮 `240s` dispatch 提前到 `180s`，用于验证 late branch 只要提前介入 `cracked-star-jar` 是否能恢复 300 秒转换。

结果仍应拒绝。60 秒、180 秒窗口与 `240s` split 一致，300 秒仍为三图 `0.0` 胜率。`cracked-star-jar` 300 秒平均存活只从 `175.125s` 微增到 `175.2584s`，两个 late failure 仍在 `230.5203s` 和 `238.3886s` 死亡，说明 late branch 本身没有在当前父策略上下文中形成可用转换。

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `180s` | `multimap_comparison_recorded_watch` | `0.3333` | `0.6667` | `0.6667` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.0` |

## Failure Analysis

300 秒失败分析仍记录 `9` 条失败局，三张 high-pressure 地图各 `3` 条。每图依旧是 `1` 条 opening failure 和 `2` 条 late failure；提前 dispatch 没有改变失败桶分布。

| Map | Win rate | Average survival | Dominant action | Failure buckets |
| --- | ---: | ---: | --- | --- |
| `soda-creek` | `0.0` | `152.2781s` | `1` / `0.3542` | `1 opening`, `2 late` |
| `caramel-workshop` | `0.0` | `158.4236s` | `5` / `0.2449` | `1 opening`, `2 late` |
| `cracked-star-jar` | `0.0` | `175.2584s` | `5` / `0.2456` | `1 opening`, `2 late` |

## 判断

- 提前到 `180s` 后 split policy 能保持多基线 no-regression，但不能恢复 `cracked-star-jar` 300 秒胜率。
- 当前 late branch 的单独 300 秒恢复信号不能通过简单 per-map dispatch 迁移到 mid-anchor parent。
- 下一步不应继续只调 split 秒数；需要检查 late branch 与 parent handoff 时的 state distribution，或转向训练期 per-map constrained repair。
- 该 run 不是 policy candidate，也不是 RL acceptance 证据。

## 输出文件

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `window_regression_vs_e30.json`
- `window_regression_vs_e30.md`
- `window_regression_vs_mid_anchor_parent.json`
- `window_regression_vs_mid_anchor_parent.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
