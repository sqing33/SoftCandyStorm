# 多图终局胜利条件分派探针

- item_id: `rl_sb3_terminal_victory_multimap_pressure_gate_w1_e30`
- gate_decision: `rl_repair_probe_gate_failed`
- 结论: `repair`

## 目标

本轮不重新训练 terminal model，而是在上一轮多图 victory path target branch 上增加 evaluation-only 分派条件：三图 `210-240s` terminal window 内，只有 `combined_pressure >= 0.25` 或 `low_health_risk >= 0.4` 时才切到 terminal branch。

该探针用于判断上一轮 `300s/soda-creek` action 1 ratio blocker 是否主要由无条件 terminal 分派造成。

## 主要结果

- terminal model: `harness/reports/2026-05-29_rl_sb3_terminal_victory_multimap_path_target_w1_e30_001/ppo_terminal_victory_multimap_path_target_w1_e30.zip`
- base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- dispatch: `210-240s`，三张 high-pressure 地图，`min_pressure = 0.25`，`min_low_health_risk = 0.4`
- `comparison_parent_60s.json`: high-pressure 胜率 `0.6667 / 0.6667 / 1.0`
- `comparison_parent_180s.json`: high-pressure 胜率 `0.3333 / 0.6667 / 0.6667`
- `comparison_parent_300s.json`: high-pressure 三图胜率仍为 `0.0 / 0.0 / 0.0`
- `window_regression_vs_parent.json`: `policy_window_regression_failed`，blocker 为 `300s/cracked-star-jar: average_survival_seconds dropped 0.4668s beyond allowed 0.0s`
- `window_regression_vs_e30.json`: `policy_window_regression_failed`，blocker 为 `300s/soda-creek: action 1 ratio increased 0.216 beyond allowed 0.2`
- `failure_analysis_300s.json`: 9 个失败局，三图都仍需要 repair
- `repair_probe_gate.json`: `rl_repair_probe_gate_failed`

## Gate 结论

pressure / low-health 条件化分派没有解除 `soda-creek` 在线动作分布 blocker，也没有产生 300 秒胜利转换；相对 parent 还新增 `cracked-star-jar` 300 秒平均生存下降 blocker。

该结果说明当前问题不是简单的“无条件 terminal 分派太宽”，而是 terminal branch 本身没有学到可泛化的 late conversion action separation。下一步不应继续只调分派阈值，应转向 per-map terminal objective、branch usage instrumentation，或重新收集更接近失败状态的 conversion target。
