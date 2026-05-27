# Route Recovery Aux Multimap Boundary Samples

## 结论

- Gate decision: `dataset_validated_not_training_gate`
- Source checkpoint: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/staged.pt`
- Source traces: `15` 条 high-pressure 60 秒 sampled traces
- Maps: `soda-creek`、`caramel-workshop`、`cracked-star-jar`
- Seeds: `62400-62404`
- Exported samples: `1676`
- Validation: `edge_recovery_samples_valid`

该批次把单 seed focused boundary samples 扩展为多图多 seed repair input。导出仍只保留 sampled trace 中 `route_recovery < 0`、`boundary.edge_risk >= 0.75`、原始动作继续顶边、目标动作不再顶边的帧。

## Source Evaluation

使用 entropy retry staged checkpoint 跑 60 秒 deterministic evaluation：

- `soda-creek`: `5` episodes，win_rate `0.4`，average_survival `40.4997s`，damage_taken_average `95.1434`，dominant action `3` ratio `0.7034`
- `caramel-workshop`: `5` episodes，win_rate `1.0`，average_survival `60.0328s`，damage_taken_average `62.8534`，top action 分布较分散但 route_recovery average `-2.1994`
- `cracked-star-jar`: `5` episodes，win_rate `0.6`，average_survival `48.7663s`，damage_taken_average `81.7640`，dominant action `7` ratio `0.7381`

## Sample Distribution

- Map distribution: `caramel-workshop` `676`，`cracked-star-jar` `558`，`soda-creek` `442`
- Time range: `4.6667-60.0328s`
- Original actions: action `3` `627`，action `7` `501`，action `1` `364`，action `5` `117`，少量 action `2/4/8`
- Target actions: action `5` `570`，action `7` `383`，action `3` `291`，action `4` `222`，action `8` `145`，少量 action `1/6`
- Target selection: `geometry_inward_non_wallward_action` `1355`，`highest_scored_non_wallward_action` `321`

## 限制

这批样本只证明多图多 seed boundary repair input 可以导出、校验和被 behavior clone dry-run 读取。它不是修复后的策略，不是 Replay 通过证据，不是 deterministic high-pressure gate，也不是 RL acceptance。

下一步可以把这批样本用于受控 opening retrain，但必须：

- 使用 `edge_recovery-min/max` 或 phase filter 明确训练窗口
- 检查 target action balance，避免把 dominant action 从 `3` 转成 `7` 或其它单向偏置
- 训练后先跑 60 秒 high-pressure 三图 gate，再考虑 180 / 300 秒

## 输出文件

- `multimap_boundary_samples.jsonl`
- `export_report.json`
- `sample_validation.json`
- `behavior_clone_dry_run.json`
- Source traces: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_traces_001/`
