# Mid Path Retention Seed 63407 Follow-Up

## 目标

将 `caramel-workshop:63407` 的 `60-300s` mid-path retention 从单 seed 扩大到 `63400-63409` 10 seed target follow-up，确认是否修复 selective opening guard 的 seed tradeoff。

## 配置

- Baseline：`harness/reports/2026-05-31_rl_terminal_sequence_selective_opening_guard_followup_001/baseline_caramel_300s_10seed.json`
- Candidate：terminal-sequence recovery policy + selective opening guard + `caramel-workshop:63407` health-retention guard
- Retention model：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Health-retention window：`60-300s`
- Target：`caramel-workshop:63407`
- Seeds：`63400-63409`
- Window：`300s`

## 结果

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| Win rate | 0.1 | 0.2 | +0.1 |
| Average survival seconds | 242.8409 | 245.5495 | +2.7086 |
| Damage taken average | 115.8589 | 111.8402 | -4.0187 |
| Average kills | 387.7 | 394.8 | +7.1 |
| Normalized action entropy | 0.8752 | 0.8624 | -0.0128 |

`window_regression_caramel_300s_10seed.json` 判定为 `policy_window_regression_passed`，blockers 为 `0`。

## Seed Deltas

| Seed | Candidate terminal |
|---:|---|
| 63402 | duration_reached @ 300.0150s |
| 63407 | duration_reached @ 300.0150s |

Candidate 保留了 selective opening guard 修成的 seed `63402`，同时恢复 baseline 原本胜利的 seed `63407`。其他 seed 仍未转胜，因此这仍是局部 repair signal。

## 结论

结论：`repair`。

`60-300s` target-specific mid-path retention 是当前最强的 `63407` 修复证据：它把 10 seed target follow-up 从失败转为 no-regression 通过，并把胜率从 `0.1` 提到 `0.2`。但它仍是 evaluation-only wrapper，不是训练出的泛化 policy，也不是 RL test Bot、stage 03 或 acceptance。

## 下一步

- 用 high-pressure 60 / 180 / 300 秒三图复查，确认该 wrapper 的 target scope 不污染已有 per-map chain 结果。
- 后续若要把它转成训练目标，应把 `60-180s` route retention 明确写入 constrained repair，而不是继续追加 low-health-only 分派。
