# Late Route Recovery Reward Profile Smoke

## 结论

- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip`
- Reward profile: `late-route-recovery`
- Warm start: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_extended_001/ppo_late_survival_reward_profile_extended.zip`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Failure case: `harness/failed_cases/fail_20260527_051_late_route_recovery_reward_profile_gap.json`

`late-route-recovery` 真实 closed-loop PPO smoke 已跑通：它从 120 秒后放大路线恢复、低血量、危险区、Boss 压力和轻量重复动作惩罚。该入口能保住 60 秒 high-pressure 三图无 repair，但不能解除 180 秒与 300 秒 blocker；不得推进 stage 03、RL acceptance、playtest 或 release。

## Training

- Timesteps: `2048`
- Train maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- Map selection: `random`
- Train seconds: `300`
- Train seeds: `62300-62320`
- Learning rate: `0.0001`
- Entropy coefficient: `0.02`
- Evaluation policy: `deterministic`

默认 60 秒 `soda-creek` training evaluation win rate 为 `0.6667`，normalized action entropy 为 `0.4590`。训练报告位于 `ppo_training_report.json`，依赖状态记录在同一报告中。

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s / 3 seed` | `0.6667` | `1.0` | `0.6667` | `multimap_comparison_recorded_not_balance_gate` |
| `180s / 3 seed` | `0.3333` | `0.6667` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |
| `300s / 3 seed` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

相对上一轮 `route_recovery` closed-loop smoke，新 profile 修复了 60 秒三图 repair 状态，并把 180 秒 `caramel-workshop` 从 `0.0` 拉到 `0.6667`；但 `cracked-star-jar` 180 秒降到 `0.0`，300 秒仍三图全 0，因此只算诊断进展。

## Failure Analysis

300 秒 9 局全部失败：

- `soda-creek`: 1 个 opening 失败、1 个 mid 失败、1 个 late 失败。
- `caramel-workshop`: 1 个 mid 失败、2 个 late 失败。
- `cracked-star-jar`: 1 个 opening 失败、2 个 mid 失败。

300 秒 route recovery hotspot 分析显示，`1100` 条采样 trace 行中有 `841` 条负 route recovery，占 `76.45%`。主要热点仍是 `boundary_edge`，动作以 action `4` 为主：`boundary_edge` 负样本 `818` 条，其中 action `4` 为 `449` 条；late bucket 最坏热点集中在贴边时继续 action `4`，尤其是 `caramel-workshop` 与 `soda-creek`。

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_late_route_recovery_reward_profile_smoke.zip`
- `ppo_late_route_recovery_reward_profile_smoke_metadata.json`
- `comparison_60s_3seed.json`
- `comparison_180s_3seed.json`
- `comparison_300s_3seed.json`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `route_recovery_hotspots_300s.json`
- `route_recovery_hotspots_300s.md`
- `traces_60s/`
- `traces_180s/`
- `traces_300s/`

## 下一步

不要继续只加大 `late-route-recovery` 权重或 timestep。下一轮应先解决贴边 action `4` 在 mid/late window 的持续选择问题：可以选择把 late-route 的负样本导出为 action-specific recovery samples，或在 closed-loop curriculum 中加入更明确的 boundary escape / route objective，同时保留当前已通过的 60 秒 hard gate 和 180 秒 regression 检查。
