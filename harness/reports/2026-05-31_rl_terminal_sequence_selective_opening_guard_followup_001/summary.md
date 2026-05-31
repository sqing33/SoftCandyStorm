# Terminal Sequence Selective Opening Guard 10 Seed Follow-Up

## 目标

复查三 seed selective opening guard 信号能否扩大到 `caramel-workshop` 300 秒 `63400-63409` 单图窗口。

## 配置

- Baseline：per-map edge branch + all-map late filter，parent model 为 `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate：`harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Opening guard：`--opening-model-targets caramel-workshop:63400`
- Map：`caramel-workshop`
- Seeds：`63400-63409`
- Window：`300s`

## 结果

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| Win rate | 0.1 | 0.1 | 0.0 |
| Average survival seconds | 242.8409 | 238.65 | -4.1909 |
| Damage taken average | 115.8589 | 116.4336 | +0.5747 |
| Average kills | 387.7 | 380.2 | -7.5 |
| Normalized action entropy | 0.8752 | 0.8615 | -0.0137 |

`window_regression_caramel_300s_10seed.json` 判定为 `policy_window_regression_failed`，blocker 为 `300s/caramel-workshop` 平均存活下降 `4.1909s`。

## Seed Deltas

| Seed | Baseline terminal | Candidate terminal | Survival delta |
|---:|---|---|---:|
| 63400 | player_health_depleted @ 213.2166s | player_health_depleted @ 213.2166s | 0.0 |
| 63401 | player_health_depleted @ 235.3546s | player_health_depleted @ 231.8206s | -3.5341 |
| 63402 | player_health_depleted @ 245.2901s | duration_reached @ 300.0150s | +54.7249 |
| 63403 | player_health_depleted @ 222.3185s | player_health_depleted @ 249.6244s | +27.3058 |
| 63404 | player_health_depleted @ 249.5243s | player_health_depleted @ 221.2183s | -28.3061 |
| 63405 | player_health_depleted @ 243.9898s | player_health_depleted @ 220.0180s | -23.9718 |
| 63406 | player_health_depleted @ 232.3540s | player_health_depleted @ 237.4551s | +5.1011 |
| 63407 | duration_reached @ 300.0150s | player_health_depleted @ 231.0204s | -68.9946 |
| 63408 | player_health_depleted @ 249.6244s | player_health_depleted @ 243.7564s | -5.8679 |
| 63409 | player_health_depleted @ 236.7216s | player_health_depleted @ 238.3553s | +1.6337 |

Candidate 把原 baseline 失败的 seed `63402` 转成胜利，但同时丢掉 baseline 原本胜利的 seed `63407`，因此 10 seed 胜率没有净增长，并出现平均存活回归。

## Trace Evidence

已为 candidate 的 9 条失败 seed 写出 failed-only traces：

- `candidate_failed_traces/caramel-workshop_seed63400_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63401_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63403_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63404_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63405_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63406_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63407_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63408_trace.json`
- `candidate_failed_traces/caramel-workshop_seed63409_trace.json`

补充 trace 对比后，seed `63407` 的退化更清楚：

- baseline `63407`：`duration_reached @ 300.0150s`，最终仍有 `74.09999` damage taken，trace 中未进入 low-health 记录。
- candidate `63407`：`player_health_depleted @ 231.0204s`，`226.0193s` 首次进入 low health，最终 top action 为 `8:0.7951`。
- 同 seed trace comparison 位于 `trace_compare_seed63407_baseline_vs_candidate.md`。
- `63402` 成功 vs `63407` 失败的跨 seed 对比位于 `trace_compare_63402_success_vs_63407_regression.md`。
- route hotspot 报告显示 `63407` 的 opening boundary/action2 热点在 baseline 和 candidate 中都存在，因此下一步不能只修 opening action2；更应检查 mid/late health retention 和低血恢复分派。

## 结论

结论：`repair`，但 10 seed follow-up 拒绝扩大推进。

Selective opening guard 的三 seed 信号是真实的，但目前像 seed-local conversion tradeoff：它修复 `63402`，却破坏 `63407`，并让 10 seed 平均存活下降。该结果不得推进为 RL test Bot、stage 03、acceptance 或更大矩阵候选。

## 下一步

- 对比 seed `63402` 成功 trace 与 seed `63407` 新失败 trace，确认 terminal-sequence checkpoint 是替换了胜利路径，还是把低血量 / hazard 恢复推迟到另一个失败面。
- 将 selective opening guard 从单 seed 扩展为更细 state-conditioned dispatch 前，必须先设计 seed `63407` mid/late health-retention guard。
- 后续复跑仍必须使用 10 seed target follow-up 加 60 / 180 / 300 秒 high-pressure no-regression。
