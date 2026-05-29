# SB3 Recovery Target Scope Filter Smoke

## 结论

- Decision: `sb3_recovery_target_scope_filter_smoke_passed_not_policy_gate`
- Scope: `risk_recovery_supervision` only, `cracked-star-jar`, `180-300s`
- Target mode: `top_k_scores`
- Overridden samples: `210`
- Map-scoped out risk samples: `214`
- Source-scoped out recovery samples: `2693`
- Fallback one-hot count: `0`

本 smoke 验证 `distill_behavior_clone_to_sb3.py` 的 recovery target override 已能按地图和时间窗收窄作用范围。它只把 `cracked-star-jar` 的 late risk recovery rows 覆写为 repair soft target，其他地图的 risk rows、edge recovery rows 和普通 retention rows 均保留 base teacher target。

## 为什么需要

上一轮 source-filtered weight sweep 证明全局 risk sample weight 会移动失败面：`w10` 有 `cracked-star-jar` 300 秒局部胜利信号，但破坏 `soda-creek` opening / mid 和 `caramel-workshop` 180 秒 retention；`w7` / `w5` 降低 blocker 后又失去 300 秒胜利。因此下一轮不能继续调全局权重，必须支持 map / phase scoped action-separation objective。

## 结果

- `recovery_target_override.overridden_sample_count = 210`
- `recovery_target_override.soft_sample_count = 210`
- `recovery_target_override.map_scoped_out_sample_count = 214`
- `recovery_target_override.source_scoped_out_sample_count = 2693`
- `recovery_target_override.average_nonzero_actions = 2.5381`
- `sample_path_weights` 仍保留 drift rows `40x` 与 clean risk rows `10x`

该模型只训练 `1` epoch，用于验证数据路径和报告字段，不是 policy candidate、stage 03 证据或 RL acceptance 证据。后续若要评估策略效果，必须重新跑 full-anchor alignment、60 / 180 / 300 秒 high-pressure、e30 + parent required no-regression、failure analysis 和 repair gate。
