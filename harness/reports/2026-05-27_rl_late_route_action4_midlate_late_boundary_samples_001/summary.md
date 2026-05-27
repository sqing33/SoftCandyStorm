# Late Boundary Recovery Samples From Action4 Mid/Late Ablation

## 结论

- Gate decision: `late_boundary_recovery_samples_exported_not_policy_gate`
- Source policy: `harness/reports/2026-05-27_rl_late_route_action4_midlate_ablation_001/action4_w0_5/staged.pt`
- Related failure: `harness/failed_cases/fail_20260527_052_late_route_action4_midlate_ablation_gap.json`
- Sample path: `harness/reports/2026-05-27_rl_late_route_action4_midlate_late_boundary_samples_001/late_boundary_recovery_samples.jsonl`

本轮基于 `action4_w0_5` staged checkpoint 的 300 秒三图失败，重新跑 high-pressure 5 seed failed-only evaluation traces，并开启 `--trace-include-observation` 与 `trace-sample-stride=10`。随后只从 `180-300s`、`route_recovery < 0`、`boundary.edge_risk >= 0.75`、原始动作继续顶边的 sampled trace 行中导出 late boundary recovery 样本。

这批输出只是 repair training input，不是 policy checkpoint、不是 Replay，也不是 high-pressure gate 通过证据。

## Source Evaluation

| Map | Seeds | Seconds | Win rate | Avg survival | Dominant action | Entropy |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `soda-creek` | `5` | `300` | `0.0` | `137.6423s` | action `3` `0.3091` | `0.7703` |
| `caramel-workshop` | `5` | `300` | `0.0` | `221.4517s` | action `3` `0.3213` | `0.7329` |
| `cracked-star-jar` | `5` | `300` | `0.0` | `184.4544s` | action `5` `0.2634` | `0.8364` |

15 条 failed-only trace 全部写入 observation，可用于监督样本导出。

## Export

- Decision: `route_recovery_samples_exported`
- Source traces: `15`
- Inspected trace rows: `8173`
- Negative route recovery rows: `1055`
- Boundary hotspot rows: `1027`
- Outside time window rows: `6816`
- Exported samples: `1001`
- Phase duration conditioning: `300s`

| Distribution | Counts |
| --- | --- |
| Map | `{"caramel-workshop": 441, "cracked-star-jar": 370, "soda-creek": 190}` |
| Original actions | `{"2": 1, "3": 293, "4": 124, "5": 262, "6": 43, "7": 223, "8": 55}` |
| Target actions | `{"1": 304, "2": 18, "3": 202, "4": 97, "5": 14, "6": 86, "7": 227, "8": 53}` |
| Target labels | `{"geometry_inward_non_wallward_action": 838, "highest_scored_non_wallward_action": 163}` |

`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，0 error、0 warning。

## Dry Run

`train_behavior_clone.py --dry-run` 使用 `gru context8`、`map-conditioning=one_hot`、`time-phase-conditioning=one_hot`、`--time-phase-filter late`、`--recovery-soft-target top_k_scores` 和 `per_map_uniform_present` 动作分布正则完成数据读取：

- Gate decision: `dataset_validated_not_training_gate`
- Samples: `1001`
- Edge recovery samples: `1001`
- Soft recovery samples: `1001`
- Average nonzero soft target actions: `2.8372`
- Phase distribution: late `100%`

诊断 flags：

- `high_action_persistence`: 连续样本目标动作重复较高，后续训练要防止 deterministic target bias。
- `map_sample_imbalance`: `soda-creek` 只有 `18.98%`，下一轮训练必须关注三图偏移。

## 下一步

这批样本比上一批 action4-only 样本更适合 late-only 或 closed-loop boundary escape 实验，因为它覆盖 action `3/5/7/4` 多种顶边失败动作，并且全部落在 `180-300s` late phase。下一轮训练仍应保留 60 秒 hard gate、180 秒 regression 与 300 秒三图 probe；如果 `soda-creek` 或 opening 回归，应先补充 soda late 样本或降低样本权重。

## 输出文件

- `source_comparison_300s_obs.json`
- `traces_300s_obs/`
- `late_boundary_recovery_samples.jsonl`
- `sample_export.json`
- `sample_export.md`
- `sample_validation.json`
- `sample_validation.md`
- `behavior_clone_dry_run.json`
