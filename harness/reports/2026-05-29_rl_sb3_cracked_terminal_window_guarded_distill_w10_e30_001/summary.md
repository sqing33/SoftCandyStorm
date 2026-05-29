# SB3 Cracked Terminal Window Guarded Distill W10 E30

## 结论

- Decision: `action_distribution_guard_failed`
- Scope: all validation slices
- Model: `ppo_cracked_terminal_window_guarded_distill_w10_e30.zip`
- Training: same terminal-window `w10` distillation setup as the previous `w10` probe

该 probe 复用 `cracked-star-jar` `210-240s` terminal-window clean risk rows、`10x` risk row weight 与 `40x` mid-anchor drift rows，只新增 action-distribution guard：

- max dominant ratio: `0.45`
- min normalized argmax entropy: `0.55`
- min sample count: `24`
- scope: `overall,sample_sources,sample_path_weights,map_time_buckets`

结果显示 guard 失败，但 blocker 来自 `anchor_drift_diagnostic` / 对应 `sample_path_weight` 小切片：`36` 条 validation samples 中 action `8` 占 `0.8889`，normalized argmax entropy 为 `0.1872`。这是 top drift rows 本身的刻意集中修复信号，不是 `caramel-workshop` 60 秒在线 dominant-action blocker。

## 解读

全作用域 guard 过于保守，会把故意集中的辅助 repair slice 当成动作塌缩。后续使用该 guard 时，需要按 probe 目的选择 scope；对于 terminal-window online blocker，应优先看 `overall` 与 `map_time_buckets`，并把 `sample_sources` / `sample_path_weights` 留作诊断信息而不是硬门禁。

## 限制

- 这是 distillation evidence guard 诊断，不是 high-pressure 或 RL acceptance。
- 该结果不证明 terminal-window repair 已修复。
- 后续仍必须运行 fixed-window high-pressure、e30 + parent no-regression、failure analysis 与 repair-probe gate。
