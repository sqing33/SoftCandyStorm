# Late Route Action4 Repair Samples

## 结论

- Gate decision: `repair_samples_exported_not_policy_gate`
- Source checkpoint: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip`
- Related failure: `fail_20260527_051`
- Sample path: `harness/reports/2026-05-27_rl_late_route_action4_samples_001/mid_late_action4_samples.jsonl`

本轮基于 `late-route-recovery` smoke 的 300 秒失败结论，重新跑三图 300 秒 failed-only evaluation traces，并启用 `--trace-include-observation`。随后只导出 `60-300s`、原始 action `4`、`boundary.edge_risk >= 0.75` 且 `route_recovery < 0` 的贴边修复样本。

该输出只是 repair training input，不是 policy checkpoint、不是 Replay、不是 high-pressure gate 通过证据。

## Source Evaluation

| Map | Seeds | Seconds | Win rate | Avg survival |
| --- | ---: | ---: | ---: | ---: |
| `soda-creek` | `3` | `300` | `0.0` | `113.9497s` |
| `caramel-workshop` | `3` | `300` | `0.0` | `176.7107s` |
| `cracked-star-jar` | `3` | `300` | `0.0` | `71.5437s` |

9 条 failed-only trace 全部写入 observation，可用于监督样本导出。

## Export

- Decision: `route_recovery_samples_exported`
- Source traces: `9`
- Inspected trace rows: `1100`
- Negative route recovery rows: `471`
- Boundary hotspot rows: `463`
- Outside time window rows: `539`
- Original action filtered rows: `209`
- Exported samples: `254`
- Time range: `60.9994s-214.1501s`
- Phase duration conditioning: `300s`

| Distribution | Counts |
| --- | --- |
| Map | `{"caramel-workshop": 158, "soda-creek": 65, "cracked-star-jar": 31}` |
| Original actions | `{"4": 254}` |
| Target actions | `{"8": 135, "3": 88, "5": 25, "7": 6}` |
| Target labels | `{"geometry_inward_non_wallward_action": 141, "highest_scored_non_wallward_action": 113}` |

`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，0 error、0 warning。

## Dry Run

`train_behavior_clone.py --dry-run` 使用 `gru context8`、`map-conditioning=one_hot`、`time-phase-conditioning=one_hot`、`--recovery-soft-target top_k_scores` 与 `per_map_uniform_present` 动作分布正则完成数据读取：

- Gate decision: `dataset_validated_not_training_gate`
- Samples: `254`
- Edge recovery samples: `254`
- Observation length: `145`
- Soft recovery samples: `254`
- Average nonzero soft target actions: `2.5551`
- Fully seeded context ratio: `0.9173`
- Late low-health sample ratio: `0.6969`

诊断 flags：

- `high_action_persistence`: 连续样本目标动作重复较高，后续训练要防止 deterministic target bias。
- `map_sample_imbalance`: `caramel-workshop` 占 `62.20%`，后续 map-conditioned 训练必须关注三图偏移。

## 下一步

这批样本适合做小权重 mid/late action `4` 修复消融。训练时应保留 60 秒 hard gate、180 秒 regression 与 300 秒三图 probe；如果训练后 `cracked-star-jar` 或 opening 回归，应先扩大非 caramel 样本或拆分 per-map/per-phase 子模型，而不是继续提高样本权重。

## 输出文件

- `evaluation_soda_creek_300s_obs.json`
- `evaluation_caramel_workshop_300s_obs.json`
- `evaluation_cracked_star_jar_300s_obs.json`
- `traces_300s_obs/`
- `mid_late_action4_samples.jsonl`
- `sample_export.json`
- `sample_export.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
