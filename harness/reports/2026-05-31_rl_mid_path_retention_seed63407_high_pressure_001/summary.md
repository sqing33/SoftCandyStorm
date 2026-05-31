# Mid Path Retention Seed 63407 High-Pressure Check

## 目标

复查 `caramel-workshop:63407` 的 target-specific mid-path retention wrapper 是否会污染 high-pressure 三图 `60/180/300s` 固定窗口。

## 配置

- Baseline：`harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_comparison_{60s,180s,300s}.json`
- Candidate：terminal-sequence recovery policy + selective opening guard + `caramel-workshop:63407` health-retention guard
- Health-retention target：`caramel-workshop:63407`
- Health-retention window：`60-300s`
- High-pressure seed window：`63400-63402`
- Maps：`soda-creek`、`caramel-workshop`、`cracked-star-jar`

## 结果

| Window | soda-creek | caramel-workshop | cracked-star-jar |
|---|---:|---:|---:|
| 60s win rate | 1.0 | 1.0 | 1.0 |
| 180s win rate | 1.0 | 1.0 | 1.0 |
| 300s win rate | 1.0 | 0.3333 | 1.0 |

`window_regression_vs_per_map_chain.json` 判定为 `policy_window_regression_passed`，blockers 为 `0`。

因为本轮 high-pressure 使用 seeds `63400-63402`，`caramel-workshop:63407` 的 health-retention target 不会触发；该报告主要证明新增 wrapper 的 target scope 和 provenance 没有污染现有三 seed high-pressure 信号。

## 结论

结论：`repair`。

当前可保留的结论是：`63407` 的 mid-path retention 在 10 seed target follow-up 中有效，并且 target-specific wrapper 不影响既有 `63400-63402` high-pressure no-regression。它仍不是泛化 policy、RL test Bot、stage 03 或 acceptance 证据。

## 下一步

- 将 `63407` 的修复信号转化为训练期 `60-180s` route retention / path preservation objective。
- 继续把 10 seed target follow-up 与 high-pressure `60/180/300s` no-regression 作为硬门槛。
