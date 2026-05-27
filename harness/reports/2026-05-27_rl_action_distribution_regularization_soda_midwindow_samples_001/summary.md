# Action Distribution Regularization Soda Midwindow Samples

## 结论

- Gate decision: `repair_samples_exported_not_policy_gate`
- Source checkpoint: `harness/reports/2026-05-27_rl_action_distribution_regularization_opening_ablation_001/per_map_uniform_0_2/staged.pt`
- Source failure: `fail_20260527_046`
- Sample path: `harness/reports/2026-05-27_rl_action_distribution_regularization_soda_midwindow_samples_001/soda_midwindow_route_recovery_samples.jsonl`

本轮从 `per_map_uniform_0_2` 的 `soda-creek` 180 秒失败评估重新导出带 observation 的失败 trace，并从 `50-80s` 路线恢复窗口提取状态条件化 repair samples。导出成功，但样本只来自 seed `62404`，因此只能作为下一轮 targeted repair 输入，不能作为 policy gate。

## Source Evaluation

- Map: `soda-creek`
- Seeds: `62400-62404`
- Seconds: `180`
- Win rate: `0.0`
- Average survival: `52.6997s`
- Damage taken average: `120.3327`
- Trace stride: `10`
- Trace failed only: `true`
- Trace include observation: `true`

5 个 seed 全部失败，只有 seed `62404` 存活超过 `80s`；因此 `50-80s` repair samples 全部来自该 seed。

## Export

- Decision: `route_recovery_samples_exported`
- Source traces: `5`
- Inspected trace rows: `798`
- Negative route recovery rows: `54`
- Boundary hotspot rows: `52`
- Exported samples: `51`
- Time range: `50.3329s-79.9991s`
- Phase duration conditioning: `300s`

| Distribution | Counts |
| --- | --- |
| Map | `{"soda-creek": 51}` |
| Original actions | `{"1": 24, "6": 27}` |
| Target actions | `{"2": 27, "5": 24}` |
| Target labels | `{"geometry_inward_non_wallward_action": 51}` |

`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`。

## Phase Dry Runs

| Phase | Samples | Edge recovery samples | Soft recovery samples | Time range |
| --- | ---: | ---: | ---: | --- |
| `opening` | `5787` | `399` | `399` | `0.0s-59.9994s` |
| `mid` | `9935` | `24` | `24` | `60.3328s-179.6761s` |

由于 staged policy 使用 `phase_duration_seconds = 300`，`50-60s` 样本会进入 opening 子模型，`60-80s` 样本会进入 mid 子模型。下一轮训练应同时重训 opening 与 mid，或至少先把 `60-80s` 的 24 条 mid recovery samples 用低权重/soft target 消融验证。

## 限制

- 样本来自单个 seed，覆盖面很窄。
- 样本只覆盖贴边且 `route_recovery < 0` 的 sampled trace rows。
- 当前报告只证明样本可导出、可校验、可进入 behavior clone dry-run；不证明训练后 policy 会改善。

## 输出文件

- `soda_180s_trace_eval.json`
- `traces/soda-creek_seed62400_trace.json`
- `traces/soda-creek_seed62401_trace.json`
- `traces/soda-creek_seed62402_trace.json`
- `traces/soda-creek_seed62403_trace.json`
- `traces/soda-creek_seed62404_trace.json`
- `export_report.json`
- `export_report.md`
- `soda_midwindow_route_recovery_samples.jsonl`
- `sample_validation.json`
- `sample_validation.md`
- `mixed_opening_dry_run.json`
- `mixed_mid_dry_run.json`
