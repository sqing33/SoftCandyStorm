# Route Recovery Aux Multimap Boundary Opening Smoke

## 结论

- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Staged model: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_001/staged.pt`
- 新 opening model: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_001/opening.pt`
- 沿用 mid / late：`harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt` 和 `late.pt`
- Failure case: `harness/failed_cases/fail_20260527_042_route_recovery_aux_multimap_boundary_opening_action6_bias.json`

这次 smoke 使用上一批 `1676` 条多图 boundary repair samples，并只重训 opening 子模型。训练窗口限制为 `0-60s`，实际进入 opening 训练集的样本为 `5617` 条，其中 `229` 条是 `edge_recovery_supervision_sample`，占 `4.08%`；`edge_recovery_sample_weight = 2.0` 后训练集加权 repair 比例约 `4.12%`。

## Training

- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Time phase conditioning: `one_hot`
- Phase filter: `opening`
- Edge recovery window: `0-60s`
- Class weighting: `inverse_frequency`
- Entropy regularization: `0.01`
- Final validation accuracy: `0.5494`
- Final validation entropy: `1.425587` nats

训练集 action 分布比上一轮 focused 样本更宽：action `3` 占 `0.2227`，action `5` 占 `0.1456`，action `7` 占 `0.1136`，action `6` 占 `0.1111`。这说明输入数据没有单向 target collapse，但训练后的在线策略仍可能形成新的 dominant action。

## Evaluation

60 秒 deterministic high-pressure 三图比较结果：

- `soda-creek`: win_rate `0.4`，average_survival `49.2129s`，damage_taken `106.7094`，action `6` ratio `0.7726`，normalized entropy `0.3962`，gate `comparison_recorded_needs_action_bias_repair`
- `caramel-workshop`: win_rate `1.0`，average_survival `60.0328s`，damage_taken `53.5767`，action `6` ratio `0.7349`，normalized entropy `0.4457`
- `cracked-star-jar`: win_rate `0.6`，average_survival `49.5996s`，damage_taken `87.5514`，action `6` ratio `0.7227`，normalized entropy `0.4023`

## 判断

多图 boundary samples 解决了“样本覆盖太窄”的输入问题，但这次 `inverse_frequency + entropy_regularization 0.01 + repair weight 2.0` 的组合把在线 opening 策略推向新的 action `6` dominant bias。该 checkpoint 不能进入 stage 03、180/300 秒长窗、RL acceptance 或任何发布证据。

下一步应先做参数消融，而不是继续扩大样本权重：

- 去掉或降低 `inverse_frequency`，观察 action `6` bias 是否来自类别权重过补偿
- 比较 `edge_recovery_sample_weight = 1.0 / 1.5 / 2.0`
- 保留 60 秒三图 deterministic gate 作为最小门槛
- 如果仍产生 dominant action，需要改训练目标或增加 online-prefix 历史诊断，而不是推进长窗

## 输出文件

- `opening_dry_run.json`
- `opening_training.json`
- `packaging.json`
- `high_pressure_60s_comparison.json`
- `high_pressure_60s_traces/`
