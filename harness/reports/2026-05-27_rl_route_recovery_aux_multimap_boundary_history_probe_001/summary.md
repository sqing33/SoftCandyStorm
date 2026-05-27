# Route Recovery Aux Multimap Boundary History Probe

## 结论

- Gate decision: `history_probe_recorded_watch_only`
- Model: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_ablation_001/no_class_weight_2_0/staged.pt`
- Trace target: `soda-creek` seed `62403`
- Source evaluation: `no_class_weight_2_0_soda_eval_60s.json`

本轮诊断 `no_class_weight_2_0` 的 action `6` 偏置来源。该模型在 60 秒 `soda-creek` 五 seed 中 win_rate `0.4`，seed `62403` 于 `46.7996s` 死亡；本报告只检查离线预测、nearest offline target 和 history prefix，不是策略门禁或 acceptance。

## Findings

离线全训练数据诊断没有发现 action collapse：

- Samples: `23402`
- Accuracy: `0.5888`
- Dominant predicted action: action `3` ratio `0.1732`
- Normalized predicted action entropy: `0.9336`
- Opening phase dominant predicted action: action `3` ratio `0.2943`

但在线 `soda-creek` seed `62403` 的 nearest offline target 与在线动作高度一致：

- Trace samples: `142`
- Nearest target matches online action ratio: `0.9225`
- Online action distribution: action `3` `0.0704`，action `5` `0.2042`，action `6` `0.7254`
- Nearest target distribution: action `3` `0.0986`，action `5` `0.1549`，action `4` `0.0493`，action `6` `0.6972`
- `20-40s` bucket: online action `6` `1.0`，nearest target action `6` `0.9672`
- `40-50s` bucket: online action `6` `1.0`，nearest target action `6` `0.9048`

History prefix probe 显示 cold、online-prefix 和 teacher-prefix 在 `20-40s`、`40-47s` 都选择 action `6`，说明这次不是简单的 online GRU history 锁死问题。模型在这些在线状态附近找到的离线最近邻本身也主要是 action `6`，所以后续不能只调 prefix 或清空 history。

## 判断

`inverse_frequency` 会放大 action `6` 过补偿，但去掉 class weighting 后，剩余问题来自在线状态分布：策略在 20 秒后进入了一批离线数据中本来就以 action `6` 为 target 的状态邻域，而这些 target 没有带来足够 route recovery。下一步应改 teacher target 或训练目标，而不是继续只调 `edge_recovery_sample_weight`。

建议下一轮：

- 从失败在线 trace 中导出 `20-47s` 的 route recovery repair samples，并要求目标动作显式降低 boundary / route risk
- 对同一观察邻域检查多动作候选分数，考虑 soft target 或 top-k target，而不是硬 argmax action
- 保留 `class_weighting = none`
- 继续用 60 秒 high-pressure 三图 deterministic gate，不能推进 180/300 秒或 RL acceptance

## 输出文件

- `no_class_weight_2_0_soda_eval_60s.json`
- `no_class_weight_2_0_soda_traces/`
- `offline_policy_diagnostic.json`
- `offline_policy_diagnostic.md`
- `trace_dataset_nearest_soda_62403.json`
- `trace_dataset_nearest_soda_62403.md`
- `history_context_probe_soda_62403.json`
- `history_context_probe_soda_62403.md`
