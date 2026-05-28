# Curriculum Stage 01 Opening Repair

## 结论

- Gate decision: `curriculum_stage01_opening_recorded_needs_late_repair`
- Model: `stage_01_opening_lt_60.zip`
- Reward profile: `late-route-recovery`
- Warm start: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip`
- Failure case: `harness/failed_cases/fail_20260528_064_curriculum_stage01_opening_longrun_gap.json`

本阶段按课程计划只处理 `fail_20260528_063` 中的 `opening_lt_60` failures，训练地图为 `cracked-star-jar,soda-creek`，训练窗口 `60s`，PPO `2048` timesteps，`ent_coef=0.02`。该阶段是 closed-loop PPO repair experiment，不是 acceptance evidence。

结果：opening 短窗修复成功，但长窗仍失败。60 秒 high-pressure 三图达到 `1.0/1.0/1.0`，180 秒为 `0.6667/1.0/1.0`；300 秒三图仍为 `0.0/0.0/0.0`，不能推进 stage 03、RL acceptance、playtest 或 release。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `213.7723s` | mid `1`, late `2` | action `7` `56.89%` | `0.4703` |
| `caramel-workshop` | `0.0` | `215.8505s` | late `3` | action `7` `38.57%` | `0.6019` |
| `cracked-star-jar` | `0.0` | `235.5752s` | late `3` | action `7` `46.22%` | `0.4869` |

相比 `fail_20260528_063`，本阶段移除了 300 秒评估中的 opening deaths，并把 `soda-creek` / `cracked-star-jar` 平均失败时间推迟，但失去了 `caramel-workshop` 和 `cracked-star-jar` 的 300 秒 `0.2` 胜率信号。主要新风险是 action `7` dominant。

## 判断

- Stage 01 可作为 opening repair evidence，但不能作为长窗 policy candidate。
- Stage 02 如果继续执行，必须显式验证 60/180/300 秒三窗，不能只看 late repair。
- 若 stage 02 继续放大 action `7` 或损伤 60/180 秒，应记录 failure case 并回到 reward / curriculum 设计。

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `stage_01_opening_lt_60.zip`
- `stage_01_opening_lt_60_metadata.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
