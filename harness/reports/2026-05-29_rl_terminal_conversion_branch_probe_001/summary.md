# RL Terminal Conversion Branch Probe

## 结论

- Decision: `diagnostic_no_conversion_e30_base`
- Base model: `ppo_supervised_realign_full_anchor_drift_w40_e30.zip`
- Terminal model: `ppo_cracked_terminal_window_risk_distill_w10_e30.zip`
- Adapter mode: `terminal_conversion_branch`
- Scope: `cracked-star-jar`, `210-240s`

本次用 e30 checkpoint 作为 base，只在 `cracked-star-jar` 的 `210-240s` 窗口切到 terminal-window w10 model。该诊断确认显式 branch 可以避免 w10 全局替换造成的 online action-distribution delta blocker，但不能恢复 300 秒 high-pressure 胜率，也不能相对 mid-anchor parent 保持 no-regression。

## Fixed-window High-pressure

| Window | Gate | Avg Win | Avg Survival | Repair Maps |
|---|---|---:|---:|---|
| `60s` | `multimap_comparison_recorded_watch` | `0.5556` | `48.3588s` | none |
| `180s` | `multimap_comparison_recorded_watch` | `0.5556` | `118.3718s` | none |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `157.2452s` | `soda-creek`, `caramel-workshop`, `cracked-star-jar` |

300 秒三图胜率仍为 `0.0 / 0.0 / 0.0`。`cracked-star-jar` 平均存活为 `170.5025s`，只比 e30 baseline 的 `170.4247s` 增加 `0.0778s`。

## No-regression

- vs e30: `policy_window_regression_passed`
- vs e30 online action-distribution delta: `policy_window_regression_passed`
- vs mid-anchor parent: `policy_window_regression_failed`，`9` blockers
- Repair gate: `rl_repair_probe_gate_failed`，`9` blockers

e30-base branch 的主要价值是证明 wrapper 没有复现 w10 全局模型的 online action-distribution 漂移；但它在 60 / 180 秒继承 e30 而非 parent，因此不能作为 parent-preserving 分支。

## Failure Analysis

`failure_analysis_300s.json` 记录 `9` 个失败局，每张图各 `3` 个：

- `soda-creek`: `2` 个 late death，`1` 个 opening death
- `caramel-workshop`: `2` 个 late death，`1` 个 opening death
- `cracked-star-jar`: `2` 个 late death，`1` 个 opening death

## 判断

- 显式 terminal-conversion branch 的调度逻辑可用。
- 只把 terminal model 限定到 `cracked-star-jar 210-240s` 不能完成 300 秒 long-run conversion。
- e30-base 版本不能替代 parent-preserving repair，因为它相对 mid-anchor parent 触发多项短窗和长窗回归。
- 后续应优先查看 parent-base 变体报告，并停止把当前 wrapper 当作 policy candidate 或 RL acceptance 证据。

## 产物

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_e30.json`
- `window_regression_vs_parent.json`
- `window_regression_action_delta_vs_e30.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
