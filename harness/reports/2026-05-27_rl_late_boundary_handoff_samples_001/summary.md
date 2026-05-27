# Late Boundary Handoff Recovery Samples

## 结论

- Gate decision: `handoff_recovery_samples_exported_not_policy_gate`
- Source probe: `harness/reports/2026-05-27_rl_late_boundary_opening_wrapper_probe_001/summary.md`
- Related failure: `harness/failed_cases/fail_20260527_055_late_boundary_opening_wrapper_fallback_gap.json`
- Sample path: `harness/reports/2026-05-27_rl_late_boundary_handoff_samples_001/handoff_recovery_samples.jsonl`

本轮基于 stage01 SB3 opening wrapper + late boundary fallback 的 300 秒失败面，重新跑 high-pressure 三图 `62400-62404` failed-only traces，并开启 `--trace-include-observation` 与 `trace-sample-stride=10`。随后只从 `60-180s`、负 `route_recovery`、`boundary.edge_risk >= 0.75`、原动作继续顶边的 sampled trace 行中导出 handoff recovery 样本。

这批输出只是 fallback / mid-window repair training input，不是 policy checkpoint、不是 Replay，也不是 high-pressure gate 通过证据。

## Source Evaluation

| Map | Seeds | Seconds | Win rate | Avg survival | Dominant action | Entropy |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `soda-creek` | `5` | `300` | `0.0` | `130.4360s` | action `7` `0.4096` | `0.5375` |
| `caramel-workshop` | `5` | `300` | `0.0` | `200.4405s` | action `7` `0.4130` | `0.5524` |
| `cracked-star-jar` | `5` | `300` | `0.2` | `184.9634s` | action `7` `0.5511` | `0.4428` |

14 条 failed-only trace 全部写入 observation，可用于监督样本导出。

## Export

- Decision: `route_recovery_samples_exported`
- Source traces: `14`
- Inspected trace rows: `6860`
- Negative route recovery rows: `2616`
- Boundary hotspot rows: `2520`
- Outside time window rows: `3364`
- Exported samples: `2438`
- Phase duration conditioning: `300s`

| Distribution | Counts |
| --- | --- |
| Map | `{"caramel-workshop": 1221, "cracked-star-jar": 655, "soda-creek": 562}` |
| Original actions | `{"2": 82, "3": 92, "4": 948, "7": 1294, "8": 22}` |
| Target actions | `{"0": 658, "1": 65, "2": 248, "3": 735, "4": 12, "5": 107, "6": 3, "7": 103, "8": 507}` |
| Target labels | `{"geometry_inward_non_wallward_action": 1206, "highest_scored_non_wallward_action": 1232}` |

`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，样本覆盖三张高压图、seed `62400-62404`，时间范围为 `60.3328-179.6761s`。

## Dry Run

`train_behavior_clone.py --dry-run` 使用 `gru context8`、`map-conditioning=one_hot`、`time-phase-conditioning=one_hot`、`time-phase-filter=mid`、`recovery-soft-target=top_k_scores` 和 `per_map_uniform_present` 动作分布正则完成数据读取：

- Gate decision: `dataset_validated_not_training_gate`
- Samples: `2438`
- Edge recovery samples: `2438`
- Risk recovery samples: `0`
- Phase distribution: mid `100%`
- Same action ratio: `0.88`

诊断重点：

- `caramel-workshop` 占 `50.08%`，`soda-creek` 占 `23.05%`，后续训练要关注地图偏移。
- target action `0` 占 `26.99%`，说明“非顶边最高分”有时会落到 idle；训练时应保留 soft target 和动作分布正则，避免把 handoff 修复变成静止策略。

## 下一步

- 可用这批样本做 mid-only 或 fallback-only 小权重消融，但必须保留 stage01 opening wrapper、60 秒 hard gate、180 秒 regression 和 300 秒三图 probe。
- 训练前建议先限制或下调 target action `0` 的影响，或用 soft target 保留次优安全动作。
- 任何使用该样本训练出的 policy 都不能绕过 deterministic high-pressure 60/180/300 秒多图门禁。

## 输出文件

- `source_comparison_300s_obs.json`
- `traces_300s_obs/`
- `handoff_recovery_samples.jsonl`
- `sample_export.json`
- `sample_export.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
