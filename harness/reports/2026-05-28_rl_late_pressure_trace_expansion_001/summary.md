# Late Pressure Trace Expansion

## 结论

- Gate decision: `late_pressure_trace_expansion_recorded_not_training_gate`
- Source checkpoint: `harness/reports/2026-05-27_rl_route_recovery_reward_profile_smoke_001/ppo_route_recovery_reward_profile_smoke.zip`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Comparison: `comparison_300s_10seed.json`
- Trace dir: `traces_300s_obs`

本轮只扩充 180-300 秒 late pressure 失败面和 repair sample 覆盖，不训练模型、不推进 stage 03、不作为 RL acceptance。当前 checkpoint 在 high-pressure 三图、seed `62500-62509`、300 秒 deterministic 评估中仍为 `0.0` win rate，结论保持 repair。

## Source Evaluation

| Map | Seeds | Win rate | Avg survival | Failed traces |
| --- | ---: | ---: | ---: | ---: |
| `soda-creek` | `10` | `0.0` | `94.8581s` | `10` |
| `caramel-workshop` | `10` | `0.0` | `132.7262s` | `10` |
| `cracked-star-jar` | `10` | `0.0` | `135.6366s` | `10` |

Failure buckets: `soda-creek` 为 opening `5` / mid `2` / late `3`，`caramel-workshop` 为 opening `1` / mid `5` / late `4`，`cracked-star-jar` 为 opening `2` / mid `4` / late `4`。这说明 180-300 秒仍是主要修复方向之一，但 opening 和 mid regression 也还没有消失。

## Hotspots

`analyze_route_recovery_traces.py` 共检查 `30` 条 failed-only observation trace，记录 `10940` 个 sampled rows，其中 `8586` 个为负 route_recovery rows。

| Bucket | Hotspots | Main actions |
| --- | ---: | --- |
| `opening_lt_60` | `3292` | `4`, `7`, `3` |
| `mid_60_to_180` | `4207` | `4`, `7`, `3` |
| `late_180_to_300` | `1087` | `4`, `3`, `7` |

压力标签覆盖比上一轮更充足：`low_health` `933`、`hazard_pressure` `859`、`boss_pressure` `32`。这些数字是 sampled trace 诊断，不是完整 Replay。

## Samples

| Slice | Decision | Samples | Maps | Original actions | Target actions |
| --- | --- | ---: | --- | --- | --- |
| `late_boundary` | `route_recovery_samples_exported` | `1076` | `caramel-workshop`, `cracked-star-jar`, `soda-creek` | `3`, `4`, `7` | `1`, `2`, `3`, `8` |
| `late_low_health` | `route_recovery_samples_exported` | `145` | `caramel-workshop`, `cracked-star-jar`, `soda-creek` | `3`, `4`, `7` | `1`, `2`, `8` |
| `late_hazard` | `route_recovery_samples_exported` | `152` | `caramel-workshop`, `cracked-star-jar`, `soda-creek` | `3`, `4`, `7` | `1`, `2`, `3`, `8` |
| `late_boss` | `route_recovery_samples_exported` | `32` | `caramel-workshop`, `cracked-star-jar`, `soda-creek` | `3`, `4` | `1`, `8` |

四个样本文件均通过 `validate_edge_recovery_samples.py`。`late_boundary` 时间范围为 `180.0095-224.2523s`，覆盖 seed `62500,62503,62505,62506,62507,62508,62509`。

## Dry Run

`train_behavior_clone.py --dry-run` 使用 `late_boundary_recovery_samples.jsonl`、`gru context8`、map conditioning、time-phase conditioning、late phase filter、soft target 和 `per_map_uniform_present` 动作分布目标完成数据读取：

- Gate decision: `dataset_validated_not_training_gate`
- Samples: `1076`
- Edge recovery sample records: `1076`
- Observation length: `145`
- Phase distribution: late `100%`
- Target action `8`: `728 / 1076` (`67.66%`)

## 判断

- 本轮已经解决上一轮 pressure slice 样本过少的问题，尤其是 hazard 从 `0` 条提升到 `152` 条，Boss 从 `1` 条提升到 `32` 条。
- 样本仍然明显偏向 target action `8`，训练时必须保留 soft target、per-map action distribution regularization 和低权重消融纪律。
- 下一步可做 late-only 或 fallback-only 小权重消融，但必须复跑 deterministic high-pressure `60 / 180 / 300` 秒多图 gate；通过前不得进入 stage 03、RL acceptance、playtest 或 release。

## 输出文件

- `comparison_300s_10seed.json`
- `traces_300s_obs/`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `late_boundary_recovery_samples.jsonl`
- `late_boundary_export.json`
- `late_boundary_validation.json`
- `late_low_health_recovery_samples.jsonl`
- `late_hazard_recovery_samples.jsonl`
- `late_boss_recovery_samples.jsonl`
- `behavior_clone_dry_run.json`
