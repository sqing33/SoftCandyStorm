# SB3 Cracked Late Scoped Risk Distill W10 E30

## 结论

- Decision: `rl_repair_probe_gate_failed`
- Model: `ppo_cracked_late_scoped_risk_distill_w10_e30.zip`
- Scoped repair rows: `210` clean `cracked-star-jar` `180-300s` risk recovery samples
- Anchor drift alignment: `passed`
- Full-anchor alignment: `passed`
- 300s high-pressure: `0.0 / 0.0 / 0.0`
- Repair gate blockers: `8`

该 probe 证明 map / phase scoped risk recovery distillation 能保留离线 anchor alignment，并显著减少全局 source-filtered `w10` 的回归数量；但它仍未把 `cracked-star-jar` 300 秒 late-window 修复转成胜利，且相对 parent 仍有 opening / mid / dominant-action 回归。因此不能作为 policy candidate、stage 03 证据或 RL acceptance 证据。

## 训练输入

- Base distillation dataset: broad rule Bot / edge recovery / anchor drift mix
- Risk repair subset: `harness/reports/2026-05-29_rl_sb3_risk_recovery_cracked_late_scope_samples_001/risk_recovery_samples_cracked_late.jsonl`
- Recovery override: `top_k_scores`
- Override scope: `risk_recovery_supervision`, `cracked-star-jar`, `180-300s`
- Sample path weights:
  - mid anchor drift rows: `40x`
  - cracked late risk rows: `10x`

`distillation_report.json` 记录总样本 `36836`，其中 `risk_recovery_sample_records = 210`。`recovery_target_override.overridden_sample_count = 210`，`soft_sample_count = 210`，`fallback_one_hot_count = 0`，说明本轮只对目标 scoped risk rows 生效。

## 离线对齐

| Check | Decision | Mean KL | Argmax Agreement |
|---|---|---:|---:|
| anchor drift | `behavior_clone_anchor_alignment_within_thresholds` | `0.020786` | `0.97` |
| full anchor | `behavior_clone_anchor_alignment_within_thresholds` | `0.125045` | `0.8121` |

离线对齐通过只说明 supervised re-alignment 没有明显破坏 behavior-clone anchor；它不等价于 high-pressure policy gate。

## High-Pressure 对比

| Window | soda-creek | caramel-workshop | cracked-star-jar | Gate |
|---|---:|---:|---:|---|
| 60s | `0.3333` | `0.6667` | `1.0` | `multimap_comparison_recorded_watch` |
| 180s | `0.3333` | `0.6667` | `1.0` | `multimap_comparison_recorded_watch` |
| 300s | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

300 秒平均存活为 `soda-creek 151.8447s`、`caramel-workshop 152.4001s`、`cracked-star-jar 224.5857s`。相比全局 source-filtered `w10`，本轮没有恢复 cracked-star-jar 300 秒胜率，但保住了更多 300 秒平均存活与 no-regression 项。

## No-Regression

- vs e30: `policy_window_regression_failed`，`2` blockers
- vs parent: `policy_window_regression_failed`，`6` blockers

主要 blocker：

- `180s/cracked-star-jar` dominant action ratio 增幅略高于 `0.2`
- `180s/soda-creek` 相对 e30 平均存活下降 `8.3443s`
- `180s/soda-creek` 相对 parent 平均存活下降 `41.0798s`
- `60s/soda-creek` 相对 parent 胜率下降 `0.3334`
- `300s/caramel-workshop` 相对 parent 平均存活下降 `6.0235s`

## Failure Analysis

`failure_analysis_300s.json` 记录 `9` 个失败局：

- `soda-creek`: `3` failures，`2` 个 late death，`1` 个 opening death
- `caramel-workshop`: `3` failures，`2` 个 late death，`1` 个 opening death
- `cracked-star-jar`: `3` failures，全部为 `late_180_to_300`

`cracked-star-jar` 的平均失败时间已推到 `224.5856s`，说明 scoped risk rows 的 late repair 信号存在；但当前 shared PPO 仍无法在不破坏 parent preservation 的情况下完成 terminal conversion。

## 下一步

- 不要继续简单提高 `cracked-star-jar` scoped risk weight。
- 下一轮应把 late repair objective 与 opening / mid retention 拆开，优先保护 `soda-creek` `60s` 和 `180s`。
- 可以尝试更窄的 `cracked-star-jar` `210-240s` / low-health / boss-pressure subset，或显式 terminal-conversion branch，但必须继续保留 e30 + parent required no-regression gate。

## 产物

- `distillation_report.json`
- `anchor_drift_alignment.json`
- `full_anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `window_regression_vs_e30.json`
- `window_regression_vs_e30.md`
- `window_regression_vs_parent.json`
- `window_regression_vs_parent.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
