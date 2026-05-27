# Recovery Soft Target Opening Ablation

## 结论

- Gate decision: `ablation_recorded_needs_policy_repair`
- Variant: `soft_topk_0_6`
- Recovery soft target: `top_k_scores`
- Primary mass: `0.6`
- Top-k: `3`
- Failure case: `harness/failed_cases/fail_20260527_044_recovery_soft_target_opening_action3_bias.json`

本轮使用同一 opening 混合数据集训练 soft/top-k recovery target opening subpolicy，再与既有 `mid.pt` / `late.pt` 打成 staged checkpoint，只运行 60 秒 high-pressure 三图 deterministic comparison。

## Training

- Sample count: `5760`
- Edge recovery samples: `372`
- Soft sample count: `372`
- Fallback one-hot count: `0`
- Average nonzero actions: `1.1172`
- Validation accuracy: `0.5486`
- Validation entropy nats: `1.442279`

## 60s High-Pressure Comparison

| Map | Win rate | Avg survival | Damage avg | Dominant action | Normalized entropy | Inner gate |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| `soda-creek` | `0.6` | `49.0996s` | `87.7740` | action `3` `0.5637` | `0.5890` | `comparison_recorded_not_balance_gate` |
| `caramel-workshop` | `0.8` | `54.8128s` | `68.6900` | action `3` `0.7582` | `0.4126` | `comparison_recorded_needs_action_bias_repair` |
| `cracked-star-jar` | `0.8` | `53.4862s` | `76.7954` | action `3` `0.6079` | `0.5258` | `comparison_recorded_not_balance_gate` |

Overall gate decision is `multimap_comparison_recorded_needs_policy_repair` with `repair_maps = ["caramel-workshop"]`. Minimum policy win rate improved to `0.6`, but the action-distribution gate still blocks progression.

## 判断

Soft/top-k targets 相比上一轮 hard-label online route-risk ablation 改善了 `soda-creek` 短窗生存表现（win rate `0.4` -> `0.6`，average survival `40.8197s` -> `49.0996s`）。但 deterministic policy 仍然向 action `3` 偏移，且 `caramel-workshop` 以 `0.7582` 跨过 dominant-action repair 阈值。

这仍是有价值的 repair evidence，不是 policy candidate。下一步不应进入 180/300 秒评估；更合适的方向是 per-map action diversity constraint、更强的 action-distribution regularization，或改用能采样更宽 safe-action set 的 teacher target，而不是继续依赖当前 top-k score list。

## 输出文件

- `soft_topk_0_6/opening_training.json`
- `soft_topk_0_6/opening.pt`
- `soft_topk_0_6/packaging.json`
- `soft_topk_0_6/staged.pt`
- `soft_topk_0_6/high_pressure_60s_comparison.json`
