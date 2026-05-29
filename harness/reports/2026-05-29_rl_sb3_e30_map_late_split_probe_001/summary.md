# SB3 E30 Map Late Split Diagnostic

## 结论

- Decision: `sb3_e30_map_late_split_probe_rejected_no_late_conversion`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Late branch: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/ppo_e30_opening_mid_retention_late_probe.zip`
- Split: `cracked-star-jar` after `240s`
- Probe type: evaluation-only split policy diagnostic, not a trained checkpoint
- Window regression vs e30: `policy_window_regression_passed`
- Window regression vs mid-anchor parent: `policy_window_regression_passed`
- Repair probe gate: `rl_repair_probe_gate_passed_for_limited_followup`
- Failure case: `harness/failed_cases/fail_20260529_005_sb3_e30_map_late_split_probe_no_conversion.json`

本诊断用 `MapLateSplitPolicy` 验证一个更窄的问题：如果只在 `cracked-star-jar` 的 `240s` 后切到上一轮有 late conversion 信号但多基线回归的模型，能否保住 e30 / mid-anchor parent 的短中窗，同时恢复 `cracked-star-jar` 300 秒胜率。

结果应拒绝作为 repair 方向。多基线 no-regression 通过，只说明 split wrapper 没有比两个已有基线更差；但 300 秒 high-pressure 三图胜率仍全部为 `0.0`，并没有复现 late branch 单独评估时 `cracked-star-jar` 300 秒 `0.6667` 的恢复信号。原因是目标图的两个 late failure seed 分别死在 `230.5203s` 和 `237.9885s`，早于 `240s` split 阈值，late branch 根本无法介入这些局。

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `180s` | `multimap_comparison_recorded_watch` | `0.3333` | `0.6667` | `0.6667` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.0` |

## Failure Analysis

300 秒失败分析记录 `9` 条失败局，三张 high-pressure 地图各 `3` 条。每张地图都有 `1` 条 opening failure 和 `2` 条 late failure；`cracked-star-jar` 的 late failures 在 `230.5203s` 和 `237.9885s` 结束，说明 `240s` split 太晚，不能捕捉当前失败面。

| Map | Win rate | Average survival | Dominant action | Failure buckets |
| --- | ---: | ---: | --- | --- |
| `soda-creek` | `0.0` | `152.2781s` | `1` / `0.3542` | `1 opening`, `2 late` |
| `caramel-workshop` | `0.0` | `158.4236s` | `5` / `0.2449` | `1 opening`, `2 late` |
| `cracked-star-jar` | `0.0` | `175.125s` | `5` / `0.2466` | `1 opening`, `2 late` |

## 判断

- `MapLateSplitPolicy` 入口本身可用，可继续作为 evaluation-only 诊断工具。
- 当前 `240s` split 组合没有 late conversion 效果；它只是保持了 already-failing parent 的 300 秒失败状态。
- `repair_probe_gate` 通过只代表可有限跟进，不代表 repair 成功；本 run 的 failure analysis 仍要求记录失败并阻止推进为 RL acceptance 或 policy candidate。
- 下一步若继续 split 方向，应把 split 时间提前到 `180s` 或按 failure-time bucket 做 per-map dispatch 诊断；同时保留 e30 和 parent required window regression。

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
