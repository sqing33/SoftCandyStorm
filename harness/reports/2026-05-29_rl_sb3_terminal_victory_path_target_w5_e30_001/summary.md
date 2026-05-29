# 终局胜利路径目标覆写探针

- item_id: `rl_sb3_terminal_victory_path_target_w5_e30`
- gate_decision: `rl_repair_probe_gate_failed`
- 结论: `repair`

## 目标

本轮为 terminal-conversion branch 增加更明确的正例监督目标：`distill_behavior_clone_to_sb3.py` 新增 `--dataset-action-target-path`，允许在 `target-mode teacher_probs` 下只对指定 JSONL / 目录前缀样本使用数据集动作 one-hot target，其余样本继续使用 teacher probabilities。

这用于把 `cracked-star-jar` 胜利终局 `210-240s` 的 `358` 条 movement samples 转成局部 terminal action target，同时保留 parent / e30 retention anchors、risk rows 与 full-anchor 对齐约束。

## 训练输入

- base teacher: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- mid-anchor drift rows: `40x`
- `cracked-star-jar 210-240s` clean risk rows: `10x`
- victory terminal rows: `5x`
- dataset action override path: `harness/reports/2026-05-29_terminal_conversion_victory_sample_filter_smoke_001/cracked_victory_terminal_210_240.jsonl`

## 主要结果

`distillation_report.json` 记录 `dataset_action_target_override.overridden_sample_count = 358`，`average_nonzero_actions = 1.0`，说明目标路径样本已从 teacher distribution 改为 dataset action one-hot。离线 action-distribution guard 通过。

`w5` 是本轮最保守的可审计结果：

- `anchor_drift_alignment.json`: `behavior_clone_anchor_alignment_within_thresholds`，mean KL `0.027157`，argmax agreement `0.975`
- `full_anchor_alignment.json`: `behavior_clone_anchor_alignment_within_thresholds`，mean KL `0.121041`，argmax agreement `0.8113`
- `window_regression_vs_parent.json`: `policy_window_regression_passed`
- `window_regression_vs_e30.json`: `policy_window_regression_failed`，blocker 为 `300s/soda-creek: action 1 ratio increased 0.2234 beyond allowed 0.2`
- `comparison_parent_300s.json`: high-pressure 三图胜率仍为 `0.0 / 0.0 / 0.0`
- `repair_probe_gate.json`: `rl_repair_probe_gate_failed`

## 消融对照

- `2026-05-29_rl_sb3_terminal_victory_dataset_actions_w20_e30_001`: 全局 `target-mode dataset_actions` 让 victory slice accuracy 达到 `0.9041`，但 anchor drift mean KL `1.543488`、full-anchor mean KL `0.405769`，明显破坏 retention。
- `2026-05-29_rl_sb3_terminal_victory_path_target_w20_e30_001`: 仅对胜利路径覆写 dataset action，drift alignment 通过，但 full-anchor argmax agreement `0.7781`，opening mean KL `0.287821`，仍过重。
- `2026-05-29_rl_sb3_terminal_victory_path_target_w10_e30_001`: full-anchor 只剩 `overall argmax_agreement 0.7973 below 0.8`，接近门槛但仍失败。
- `w5`: 通过 full-anchor 和 parent no-regression，但 300 秒转换没有恢复，且相对 e30 仍有 online action distribution blocker。

## Gate 结论

该功能可作为后续 terminal-conversion branch 的训练工具，但当前 checkpoint 不能推进为 policy candidate、stage 03、RL acceptance 或 release evidence。

下一步不应继续只调单一权重或 dispatch 秒数。更合理方向是扩大成功终局样本到多图 / 更多 seed，加入 pressure / low-health conversion target，并继续把 parent + e30 no-regression、online action-distribution delta、full-anchor alignment 和 repair-probe gate 作为硬门禁。
