# SB3 Cracked Terminal Window Risk Distill W10 E30

## 结论

- Decision: `rl_repair_probe_gate_failed`
- Model: `ppo_cracked_terminal_window_risk_distill_w10_e30.zip`
- Scoped repair rows: `121` clean `cracked-star-jar` `210-240s` risk recovery samples
- Anchor drift alignment: `passed`
- Full-anchor alignment: `passed`
- 300s high-pressure: `0.0 / 0.0 / 0.0`
- Repair gate blockers: `2`

该 probe 将上一轮 `180-300s` scoped subset 进一步收窄到 `210-240s` terminal-window pressure rows。它保留了离线 anchor alignment，并把 required multibaseline blockers 从上一轮的 `8` 个降到 `2` 个；但 300 秒三图仍无胜局，因此仍不能作为 policy candidate、stage 03 证据或 RL acceptance 证据。

## 样本子集

来源：`harness/reports/2026-05-29_rl_sb3_risk_recovery_cracked_terminal_window_samples_001/summary.md`

- Input clean risk rows: `424`
- Kept rows: `121`
- Scope: `cracked-star-jar`, `210-240s`
- Dropped by map: `214`
- Dropped by time window: `89`
- Validation: `risk_recovery_samples_valid`

主要 risk reasons：

- `toward_enemy_pressure`: `56`
- `toward_hazard`: `56`
- `wallward_edge`: `22`
- `toward_boss`: `1`

## 训练输入

- Base distillation dataset: broad rule Bot / edge recovery / anchor drift mix
- Risk repair subset: `risk_recovery_samples_cracked_terminal_window.jsonl`
- Recovery override: `top_k_scores`
- Override scope: `risk_recovery_supervision`, `cracked-star-jar`, `210-240s`
- Sample path weights:
  - mid anchor drift rows: `40x`
  - cracked terminal-window risk rows: `10x`

`distillation_report.json` 记录总样本 `36747`，其中 `risk_recovery_sample_records = 121`。`recovery_target_override.overridden_sample_count = 121`，`soft_sample_count = 121`，`fallback_one_hot_count = 0`。

## 离线对齐

| Check | Decision | Mean KL | Argmax Agreement |
|---|---|---:|---:|
| anchor drift | `behavior_clone_anchor_alignment_within_thresholds` | `0.021656` | `0.975` |
| full anchor | `behavior_clone_anchor_alignment_within_thresholds` | `0.113096` | `0.8204` |

相比 `180-300s` 全窗 scoped distill，full-anchor mean KL 从 `0.125045` 降到 `0.113096`，说明更窄窗口对 broad anchor 的扰动更小。

## High-Pressure 对比

| Window | soda-creek | caramel-workshop | cracked-star-jar | Gate |
|---|---:|---:|---:|---|
| 60s | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| 180s | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| 300s | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

300 秒平均存活为 `soda-creek 155.1454s`、`caramel-workshop 161.8799s`、`cracked-star-jar 226.475s`。它比上一轮 `180-300s` scoped distill 的 `176.2768s` 平均存活略高，但仍没有产生 300 秒胜局。

## No-Regression

- vs e30: `policy_window_regression_failed`，`1` blocker
- vs parent: `policy_window_regression_failed`，`1` blocker
- Repair gate: `rl_repair_probe_gate_failed`，`2` blockers

两个 blockers 都是 `60s/caramel-workshop` dominant action ratio 超出 `0.2` 阈值：

- vs e30: `+0.2268`
- vs parent: `+0.2259`

除了该动作集中度问题外，60 / 180 / 300 秒的 win rate 和 average survival no-regression 均通过。

## Failure Analysis

`failure_analysis_300s.json` 记录 `9` 个失败局：

- `soda-creek`: `3` failures，`2` 个 late death，`1` 个 opening death
- `caramel-workshop`: `3` failures，`2` 个 late death，`1` 个 opening death
- `cracked-star-jar`: `3` failures，全部为 `late_180_to_300`

`cracked-star-jar` 平均失败时间为 `226.4749s`，三个失败分别在 `221.7517s`、`217.9509s`、`239.7222s`，说明 `210-240s` subset 正好覆盖当前终局失败窗口，但 soft distillation 仍不足以完成 terminal conversion。

## 下一步

- 不要把该 checkpoint 当作可继续加长的 policy candidate。
- 若继续该方向，优先解决 `caramel-workshop` 60 秒 action-ratio blocker，再测试更明确的 terminal-conversion target。
- 下一轮可以尝试对 `210-240s` subset 降低 weight 或加入 action-distribution guard；但任何 follow-up 仍必须保留 e30 + parent required no-regression、300 秒 high-pressure 和 failure analysis。

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
