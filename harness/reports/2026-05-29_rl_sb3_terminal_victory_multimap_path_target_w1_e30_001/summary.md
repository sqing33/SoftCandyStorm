# 多图终局胜利路径目标覆写探针

- item_id: `rl_sb3_terminal_victory_multimap_path_target_w1_e30`
- gate_decision: `rl_repair_probe_gate_failed`
- 结论: `repair`

## 目标

本轮把 `--dataset-action-target-path` 从单图 `cracked-star-jar` 扩展到 high-pressure 三图 victory terminal samples。目标是在 `210-240s` terminal window 内给独立 terminal-conversion branch 更明确的胜利路径动作监督，同时继续以 `e30_mid_anchor_guarded_probe` 作为 base policy，避免破坏父分支 retention。

## 训练输入

- base teacher: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- mid-anchor drift rows: `40x`
- `cracked-star-jar 210-240s` clean risk rows: `10x`
- 多图 victory terminal rows: `1x`
- dataset action override path: `harness/reports/2026-05-29_terminal_conversion_multimap_victory_samples_001/victory_terminal_210_240.jsonl`

## 主要结果

`distillation_report.json` 记录 `dataset_action_target_override.overridden_sample_count = 1437`，说明三图 victory terminal rows 已被覆写为 dataset action one-hot target。离线 action-distribution guard 通过，overall dominant action ratio 为 `0.1611`，normalized entropy 为 `0.9376`。

- `anchor_drift_alignment.json`: `behavior_clone_anchor_alignment_within_thresholds`，mean KL `0.025888`，argmax agreement `0.96`
- `full_anchor_alignment.json`: `behavior_clone_anchor_alignment_within_thresholds`，mean KL `0.113336`，argmax agreement `0.8226`
- `comparison_parent_60s.json`: high-pressure 胜率 `0.6667 / 0.6667 / 1.0`
- `comparison_parent_180s.json`: high-pressure 胜率 `0.3333 / 0.6667 / 0.6667`
- `comparison_parent_300s.json`: high-pressure 三图胜率仍为 `0.0 / 0.0 / 0.0`
- `window_regression_vs_parent.json`: `policy_window_regression_passed`
- `window_regression_vs_e30.json`: `policy_window_regression_failed`，blocker 为 `300s/soda-creek: action 1 ratio increased 0.216 beyond allowed 0.2`
- `failure_analysis_300s.json`: 9 个失败局，三图都仍需要 repair
- `repair_probe_gate.json`: `rl_repair_probe_gate_failed`

## Gate 结论

多图 victory target 比单图 w5 略微降低了 `soda-creek` 动作分布 blocker 幅度，但没有解除 blocker，也没有产生任何 300 秒胜利转换。该 checkpoint 不能推进为 policy candidate、stage 03、RL acceptance 或 release evidence。

下一步不应继续单纯扩大 victory target 权重。更合理方向是把 terminal branch 的分派条件加入 pressure / low-health risk，或改用 per-map terminal objective，同时继续保留 parent + e30 required window regression、online action-distribution delta、full-anchor alignment 和 repair-probe gate。
