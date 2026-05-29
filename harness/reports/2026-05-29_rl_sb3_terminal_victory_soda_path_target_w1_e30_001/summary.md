# Soda Per-Map Terminal Victory Path Target Probe

- item_id: `rl_sb3_terminal_victory_soda_path_target_w1_e30`
- gate_decision: `rl_repair_probe_gate_failed`
- 结论: `repair`

## 目标

在多图 victory terminal branch 已确认“分支会介入但仍无法胜利转换”之后，本轮只对 `soda-creek` 启用 `--dataset-action-target-maps soda-creek`，验证 per-map terminal objective 是否能修复 soda 的 300 秒失败面，同时避免把 caramel / cracked 的 victory rows 硬目标混入同一 terminal branch。

## 训练输入

- base teacher: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- mid-anchor drift rows: `40x`
- `cracked-star-jar 210-240s` clean risk rows: `10x`
- 多图 victory terminal rows: `1x`
- dataset action override path: `harness/reports/2026-05-29_terminal_conversion_multimap_victory_samples_001/victory_terminal_210_240.jsonl`
- dataset action target maps: `soda-creek`

## 主要结果

离线蒸馏报告：

- `dataset_action_target_override.overridden_sample_count = 899`
- `dataset_action_target_override.map_scoped_out_sample_count = 538`
- offline action-distribution guard: `action_distribution_guard_passed`
- final validation argmax accuracy: `0.8302`

Alignment:

- `anchor_drift_alignment.json`: `behavior_clone_anchor_alignment_within_thresholds`，mean KL `0.015443`，argmax agreement `0.975`
- `full_anchor_alignment.json`: `behavior_clone_anchor_alignment_within_thresholds`，mean KL `0.074732`，argmax agreement `0.8611`

Closed-loop comparison:

- 60s high-pressure: `0.6667 / 0.6667 / 1.0`
- 180s high-pressure: `0.3333 / 0.6667 / 0.6667`
- 300s high-pressure: `0.0 / 0.0 / 0.0`
- 300s terminal usage: `167 / 43518` decisions overall；`soda-creek` 内为 `167 / 13501`

No-regression / gate:

- `window_regression_vs_e30.json`: `policy_window_regression_failed`
- blocker: `300s/soda-creek average_survival_seconds dropped 2.256s beyond allowed 0.0s`
- `repair_probe_gate.json`: `rl_repair_probe_gate_failed`

## Gate 结论

该 per-map objective 证明 `--dataset-action-target-maps` 可以正确收窄 hard target，但没有形成 300 秒胜利转换，也没有通过 e30 no-regression。它不能推进为 policy candidate、stage 03、RL acceptance 或 release evidence。

下一步不应继续在同一 210-240s soda victory rows 上微调权重；更合理方向是收集更接近 soda 失败前状态的 conversion target，或把 terminal dispatch window 前移/改成基于失败态触发，同时继续保留 parent/e30 no-regression 和 repair-probe gate。
