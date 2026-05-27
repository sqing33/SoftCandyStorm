# Late Boundary Handoff Opening Wrapper Observation Samples

## 结论

- Decision: `handoff_opening_wrapper_60_90_samples_exported_not_policy_gate`
- Source comparison: `source_comparison_180s_obs.json`
- Trace dir: `traces_180s_obs/`
- Samples: `handoff_60_90_recovery_samples.jsonl`
- Sample validation: `edge_recovery_samples_valid`
- Dry run gate: `dataset_validated_not_training_gate`

本轮复跑 `stage01 opening wrapper + handoff_mid_w0_5 fallback` 的 180 秒 high-pressure 三图 5 seed 对比，并开启 `--trace-include-observation`。policy 结果与上一轮 trace 诊断保持一致：`soda-creek` / `caramel-workshop` / `cracked-star-jar` 均为 `0.6` 胜率，gate 为 `multimap_comparison_recorded_not_balance_gate`。该复跑只用于导出训练候选样本，不是新 policy gate，也不是 RL acceptance 证据。

## Sample Export

`tools/export_route_recovery_samples.py` 新增 `--min-health-ratio`，用于过滤极低血量残局样本。本批从 `60-90s`、负 `route_recovery`、`boundary.edge_risk >= 0.75`、原动作继续顶边的 sampled trace 行中导出 `713` 条样本；`min_health_ratio=0.25` 没有过滤掉样本，导出后样本的 `health_ratio` 范围为 `0.5002-0.6650`，说明实际进入训练候选的负 route-recovery 顶边帧不是 3.7 血绝境帧。

| Metric | Value |
| --- | ---: |
| Source traces | `15` |
| Inspected rows | `6843` |
| Negative route recovery rows | `789` |
| Boundary hotspot rows | `743` |
| Exported samples | `713` |
| Low health filtered rows | `0` |

| Distribution | Counts |
| --- | --- |
| Map | `{"soda-creek": 270, "caramel-workshop": 253, "cracked-star-jar": 190}` |
| Original actions | `{"8": 343, "3": 213, "2": 107, "1": 50}` |
| Target actions | `{"7": 159, "1": 150, "4": 134, "0": 111, "3": 55, "8": 50, "6": 48, "2": 5, "5": 1}` |

## Validation And Dry Run

`tools/validate_edge_recovery_samples.py` 判定样本结构和边界动作一致性通过：`713` 条样本覆盖三张 high-pressure 图、seed `62400-62404`，时间范围 `60.3328-89.999s`。

`train_behavior_clone.py --dry-run` 使用 `gru context8`、`map-conditioning=one_hot`、`time-phase-conditioning=one_hot`、`time-phase-filter=mid`、`edge_recovery_sample_weight=0.5`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02` 和 `action_distribution_regularization=0.2 / per_map_uniform_present` 完成数据读取。该 dry run 只证明样本可被训练链路消费，不代表在线 policy 修复。

## 下一步

- 这批样本更窄地聚焦 `60-90s` 交接后贴边动作，可用于下一轮 fallback-only 或 mid-only 小权重消融。
- 训练时仍需保留 stage01 opening wrapper、60 秒 hard gate、180 秒 regression 和 300 秒三图 probe。
- 如果在线结果仍停在 `0.6/0.6/0.6` 或 300 秒全失败，应转向真正 fallback policy 约束或引入 late-window low-health / hazard / boss pressure recovery，而不是继续加大同类 handoff 样本权重。

## 输出文件

- `source_comparison_180s_obs.json`
- `traces_180s_obs/`
- `handoff_60_90_recovery_samples.jsonl`
- `sample_export.json`
- `sample_export.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
