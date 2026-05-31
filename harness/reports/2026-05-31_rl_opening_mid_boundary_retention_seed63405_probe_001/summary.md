# Opening Mid Boundary Retention Seed 63405 Probe

## 目标

验证 `opening-mid-boundary-retention` 是否能把 `retention63405` lane 从早期 boundary/path debt 中拉回，同时不放宽 `lane_action_plan_seed63405` 要求的 hard preflight。

## 配置

- Parent：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate：`ppo_opening_mid_boundary_retention_seed63405_probe.zip`
- Reward profile：`opening-mid-boundary-retention`
- Train map / seed：`caramel-workshop:63405`
- Train seconds：`180`
- Timesteps：`256`
- Anchor guard：通过，final validation mean KL `0.106725`，argmax agreement `0.8258`
- Evaluation：deterministic policy，default upgrade first option

## Target Seed Preflight

`target_seed_preflight_seed63405_retention.json` 仍失败，但失败形态发生变化：seed `63405` 从上一轮 mid-path-retention candidate 的 `138.6673s` defeat 提升到 `220.6515s` defeat，已经超过 `180s` retention 门槛；但因为 terminal_kind 仍为 `defeat`，required preflight 继续阻塞。

## 10 Seed Follow-Up

`caramel-workshop` seeds `63400-63409`、`300s` follow-up 相对 parent 通过 no-regression：

| Metric | Delta |
|---|---:|
| Win rate | `+0.1` |
| Average survival seconds | `+19.2282` |
| Dominant action ratio | `+0.0025` |
| Action distribution L1 | `0.1899` |
| Normalized entropy | `+0.0281` |

`failure_analysis_caramel_300s_10seed.json` 仍记录 `9` 个失败局：`1` 个 opening death（seed `63402`），`8` 个 late-window death。该结果说明新 profile 对 `63405` 的 retention 有正向信号，但没有解决 opening short-window 和 late terminal survival。

## Hard Gates

`repair_probe_gate.json` 判定为 `rl_repair_probe_gate_failed`，共 `6` 个 blockers：

- `retention63405` target seed preflight：seed `63405` 仍为 defeat。
- `short60` window target preflight：`60s/caramel-workshop` win rate `0.3333` < `0.6667`，average survival `49.2774s` < `55.0s`。
- high-pressure parent no-regression：`180s/cracked-star-jar` action_distribution_l1_delta `0.7526` > `0.45`。
- high-pressure parent no-regression：`300s/caramel-workshop` action_distribution_l1_delta `0.6056` > `0.45`。
- high-pressure parent no-regression：`60s/caramel-workshop` win_rate_delta `-0.3334` < `0.0`。

## 结论

结论：`repair`，但拒绝继续加长该 checkpoint，也不能推进为 policy candidate、stage 03 或 RL test Bot。

`opening-mid-boundary-retention` 证明了 seed `63405` 的 0-180 秒 boundary/path retention objective 有训练信号：同一 seed 从 `138.6673s` 拉到 `220.6515s`。但 hard gate 仍阻止推进，因为短窗 `60s/caramel-workshop` 没有修复，cross-map action distribution drift 更严重，且 `63405` 最终仍死于 late-window。下一步应把 short-window opening preservation、seed `63402` opening repair、seed `63405` late terminal survival / conversion 分开，不要直接从该 checkpoint 继续堆 timesteps。

## Failure Case

已记录 `harness/failed_cases/fail_20260531_008_opening_mid_boundary_retention_seed63405_gate_failure.json`。
