# Recovery Soft Target Entropy Opening Ablation

## 结论

- Gate decision: `ablation_recorded_regression_not_policy_gate`
- Variant: `soft_topk_entropy_0_05`
- Recovery soft target: `top_k_scores`
- Entropy regularization: `0.05`
- Failure case: `harness/failed_cases/fail_20260527_045_recovery_soft_target_entropy_opening_soda_regression.json`

本轮在 `soft_topk_0_6` 基础上只提高 entropy regularization，从 `0.01` 提到 `0.05`。目标是验证更高 per-sample policy entropy 是否能缓解 action `3` dominant。

## Training

- Sample count: `5760`
- Edge recovery samples: `372`
- Soft sample count: `372`
- Fallback one-hot count: `0`
- Validation accuracy: `0.5512`
- Validation entropy nats: `1.464027`

## 60s High-Pressure Comparison

| Map | Win rate | Avg survival | Damage avg | Dominant action | Normalized entropy |
| --- | ---: | ---: | ---: | --- | ---: |
| `soda-creek` | `0.4` | `42.7664s` | `97.8860` | action `3` `0.6697` | `0.4366` |
| `caramel-workshop` | `0.8` | `54.8128s` | `68.4033` | action `3` `0.6624` | `0.4457` |
| `cracked-star-jar` | `0.8` | `53.4862s` | `69.6381` | action `3` `0.6061` | `0.4967` |

Overall gate decision is `multimap_comparison_recorded_not_balance_gate` and `repair_maps` is empty, but this is still only a smoke-scale comparison. Minimum policy win rate regressed from `0.6` back to `0.4`.

## 判断

更高 entropy regularization 只轻微提高了 offline validation entropy，没有转化为更健康的 deterministic online action distribution。相比 `soft_topk_0_6`，`soda-creek` win rate 从 `0.6` 回退到 `0.4`，且三张地图仍都是 action `3` dominant。

这说明单独依赖 per-sample entropy regularization 对当前失败面太间接。下一轮 opening training 前，应先加入显式 action-distribution / per-map diversity constraint，或构造更宽的 safe-action teacher target。

## 输出文件

- `soft_topk_entropy_0_05/opening_training.json`
- `soft_topk_entropy_0_05/opening.pt`
- `soft_topk_entropy_0_05/packaging.json`
- `soft_topk_entropy_0_05/staged.pt`
- `soft_topk_entropy_0_05/high_pressure_60s_comparison.json`
