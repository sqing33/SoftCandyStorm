# SB3 Cracked Terminal Window Risk Distill W7 E30

## 结论

- Decision: `rl_repair_probe_gate_failed`
- Model: `ppo_cracked_terminal_window_risk_distill_w7_e30.zip`
- Scoped repair rows: `121` clean `cracked-star-jar` `210-240s` risk recovery samples
- Anchor drift alignment: `passed`
- Full-anchor alignment: `passed`
- 300s high-pressure: `0.0 / 0.0 / 0.0`
- Repair gate blockers: `6`

该 probe 将 terminal-window scoped risk rows 的 sample path weight 从 `10x` 降到 `7x`，试图消除 `w10` 的 `60s/caramel-workshop` dominant-action blocker。结果显示 `w7` 没有解除该 blocker，反而引入 `soda-creek` 180 秒与 300 秒平均存活回归，因此不应继续沿“简单降权”方向推进。

## 训练输入

- Risk repair subset: `risk_recovery_samples_cracked_terminal_window.jsonl`
- Recovery override: `top_k_scores`
- Override scope: `risk_recovery_supervision`, `cracked-star-jar`, `210-240s`
- Sample path weights:
  - mid anchor drift rows: `40x`
  - cracked terminal-window risk rows: `7x`

`distillation_report.json` 记录总样本 `36747`，`risk_recovery_sample_records = 121`，`recovery_target_override.overridden_sample_count = 121`，`fallback_one_hot_count = 0`。

## 离线对齐

| Check | Decision | Mean KL | Argmax Agreement |
|---|---|---:|---:|
| anchor drift | `behavior_clone_anchor_alignment_within_thresholds` | `0.01972` | `0.98` |
| full anchor | `behavior_clone_anchor_alignment_within_thresholds` | `0.10967` | `0.8222` |

离线对齐略优于 `w10`，但 high-pressure regression 明显变差，说明 anchor KL 继续下降不等于在线策略更好。

## High-Pressure 对比

| Window | soda-creek | caramel-workshop | cracked-star-jar | Gate |
|---|---:|---:|---:|---|
| 60s | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| 180s | `0.3333` | `0.6667` | `1.0` | `multimap_comparison_recorded_watch` |
| 300s | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

300 秒平均存活为 `soda-creek 93.0391s`、`caramel-workshop 156.0009s`、`cracked-star-jar 222.0185s`。相比 `w10`，`soda-creek` 300 秒平均存活下降约 `62.1s`，整体平均存活从 `181.1668s` 降到 `157.0195s`。

## No-Regression

- vs e30: `policy_window_regression_failed`，`3` blockers
- vs parent: `policy_window_regression_failed`，`3` blockers
- Repair gate: `rl_repair_probe_gate_failed`，`6` blockers

主要 blockers：

- `180s/soda-creek` 平均存活回退
- `300s/soda-creek` 平均存活回退
- `60s/caramel-workshop` dominant action ratio 仍略超阈值

## Failure Analysis

`failure_analysis_300s.json` 记录 `9` 个失败局。`soda-creek` 从 `w10` 的 `2` 个 late death / `1` 个 opening death 变成 `2` 个 opening death / `1` 个 late death，说明降权削弱了 60-180 / 300 秒保留，且没有帮助 terminal conversion。

## 下一步

- 不继续测试更低 terminal-window risk weight，除非先加入 action-distribution guard。
- `w10` 仍是当前更好的 terminal-window诊断输入，问题集中在 caramel 60 秒动作集中度和 300 秒缺少 terminal conversion。
- 下一轮应转向 action-distribution guard 或显式 terminal-conversion branch，而不是继续做单参数权重扫描。

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
