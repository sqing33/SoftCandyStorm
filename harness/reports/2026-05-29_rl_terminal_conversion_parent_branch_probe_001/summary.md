# RL Terminal Conversion Parent Branch Probe

## 结论

- Decision: `rl_repair_probe_gate_failed`
- Base model: `ppo_e30_mid_anchor_guarded_probe.zip`
- Terminal model: `ppo_cracked_terminal_window_risk_distill_w10_e30.zip`
- Adapter mode: `terminal_conversion_branch`
- Scope: `cracked-star-jar`, `210-240s`
- Failure case: `harness/failed_cases/fail_20260529_014_terminal_conversion_branch_no_conversion.json`

本次以 mid-anchor parent 作为 base，只在 `cracked-star-jar` 的 `210-240s` 窗口切到 terminal-window w10 model。该变体比 e30-base 更公平：它保住了 60 / 180 秒 parent 表现，也通过了相对 e30 的 no-regression；但 300 秒三图仍全为 `0.0` 胜率，并且相对 parent 在 `cracked-star-jar 300s` 平均存活下降 `0.4779s`，repair gate 仍失败。

## Fixed-window High-pressure

| Window | Gate | Avg Win | Avg Survival | Repair Maps |
|---|---|---:|---:|---|
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.7778` | `52.5144s` | none |
| `180s` | `multimap_comparison_recorded_watch` | `0.5556` | `130.3207s` | none |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `161.7829s` | `soda-creek`, `caramel-workshop`, `cracked-star-jar` |

300 秒地图结果：

- `soda-creek`: win `0.0`, average survival `152.2781s`
- `caramel-workshop`: win `0.0`, average survival `158.4236s`
- `cracked-star-jar`: win `0.0`, average survival `174.6471s`

## No-regression

- vs e30: `policy_window_regression_passed`
- vs parent: `policy_window_regression_failed`，`1` blocker
- vs parent online action-distribution delta: `policy_window_regression_failed`，同一 survival blocker
- Repair gate: `rl_repair_probe_gate_failed`，`1` blocker

唯一 parent blocker：

- `300s/cracked-star-jar`: average survival dropped `0.4779s` beyond allowed `0.0s`

## Failure Analysis

`failure_analysis_300s.json` 记录 `9` 个失败局：

- `soda-creek`: `2` 个 late death，`1` 个 opening death
- `caramel-workshop`: `2` 个 late death，`1` 个 opening death
- `cracked-star-jar`: `2` 个 late death，`1` 个 opening death

`cracked-star-jar` 的两个 late failures 分别在 `230.5203s` 和 `236.5549s`，正好落在 terminal branch 应该发挥作用的后段附近；但 terminal branch 没有把任何局转换成 300 秒胜利。

## 判断

- wrapper dispatch 本身不是 blocker。
- terminal-window w10 model 在 parent handoff 下没有提供足够 action separation 或 win conversion。
- 该方向不应继续用同一个 terminal model 调整 dispatch 秒数；需要重新训练真正的 terminal-conversion branch，或先导出成功终局状态并构造更明确的 conversion target。
- 当前产物不得作为 policy candidate、stage 03 或 RL acceptance 证据。

## 产物

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_e30.json`
- `window_regression_vs_parent.json`
- `window_regression_action_delta_vs_parent.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
