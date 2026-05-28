# Curriculum Stage 02 Late Window Repair

## 结论

- Gate decision: `curriculum_stage02_late_window_recorded_needs_policy_repair`
- Model: `stage_02_late_180_to_300.zip`
- Reward profile: `late-route-recovery`
- Warm start: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`
- Failure case: `harness/failed_cases/fail_20260528_065_curriculum_stage02_late_window_gap.json`

本阶段按课程计划处理 `fail_20260528_064` 之后仍存在的 `late_180_to_300` failures，训练地图为 `caramel-workshop,cracked-star-jar,soda-creek`，训练窗口 `300s`，PPO `2048` timesteps，`ent_coef=0.02`。该阶段是 closed-loop PPO repair experiment，不是 acceptance evidence。

结果：stage 02 保住了 stage 01 的 60 秒和 180 秒表现，并把 300 秒 `cracked-star-jar` 从 `0.0` 提到 `0.3333`；但 `soda-creek` 和 `caramel-workshop` 300 秒仍为 `0.0`，300 秒 minimum win rate 仍未达标，不能推进 stage 03、RL acceptance、playtest 或 release。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `230.2514s` | late `3` | action `7` `42.39%` | `0.4927` |
| `caramel-workshop` | `0.0` | `212.3275s` | late `3` | action `2` `58.69%` | `0.4913` |
| `cracked-star-jar` | `0.3333` | `247.6728s` | late `2` | action `7` `39.48%` | `0.4973` |

相比 stage 01，本阶段移除了 300 秒评估中的 mid failure，并把所有失败集中到 `late_180_to_300`；但 `soda-creek` / `caramel-workshop` 仍是 0 胜率，说明 late repair 只产生局部改善，还没有形成可接受的跨图长窗策略。

## 判断

- Stage 02 可作为 late-window repair evidence，但不能作为长窗 policy candidate。
- 后续不能继续简单串联 stage 03 acceptance；下一步应先定位 `soda-creek` action `7` 和 `caramel-workshop` action `2` 的 late pressure failure。
- 继续实验时仍必须固定 60/180/300 秒三窗回归检查，避免把短窗修复换成长窗单点提升。

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `stage_02_late_180_to_300.zip`
- `stage_02_late_180_to_300_metadata.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
