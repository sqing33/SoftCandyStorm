# Route Recovery Aux Online Route Risk Opening Ablation

## 结论

- Gate decision: `ablation_recorded_not_policy_gate`
- Variant: `low_weight_1_0`
- Opening model: `low_weight_1_0/opening.pt`
- Staged model: `low_weight_1_0/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_043_online_route_risk_opening_action3_bias.json`

本轮将 phase-aligned 在线 route-risk samples 以默认权重混入 opening 训练集，保留 `class_weighting = none`、`sample_weighting = none`、`edge_recovery_sample_weight = 1.0` 和 `entropy_regularization = 0.01`。目标只是验证新增在线样本能否修复上一轮 action `6` 偏置，不作为 stage 03 或 RL acceptance 证据。

## Training

- Dataset sample count: `5760`
- Edge recovery samples: `372`
- Edge recovery ratio: `0.0646`
- Map distribution: `soda-creek` `0.3474`，`caramel-workshop` `0.3309`，`cracked-star-jar` `0.3217`
- Target action `2` ratio: `0.1052`
- Validation accuracy: `0.5330`
- Validation entropy nats: `1.441764`

## 60s High-Pressure Comparison

| Map | Win rate | Avg survival | Damage avg | Dominant action | Normalized entropy |
| --- | ---: | ---: | ---: | --- | ---: |
| `soda-creek` | `0.4` | `40.8197s` | `97.4660` | action `3` `0.5911` | `0.5538` |
| `caramel-workshop` | `0.8` | `55.8795s` | `62.0700` | action `3` `0.5227` | `0.6145` |
| `cracked-star-jar` | `0.8` | `56.3195s` | `65.1147` | action `3` `0.4837` | `0.6831` |

Overall minimum policy win rate remains `0.4` and average policy win rate is `0.6667`. The comparison is still a 5-seed smoke-scale diagnostic and cannot be used as a balance or fun gate.

## 判断

新增在线 route-risk samples 确实压低了上一轮 action `6` 过补偿，但 deterministic opening policy 转为 action `3` dominant。`soda-creek` 仍停在 `0.4` win rate，且相比之前 no-class-weight `2.0` boundary ablation 出现存活回退（`46.3663s` -> `40.8197s`）。

这说明当前单标签 repair samples 对定位失败面有价值，但不足以直接作为监督目标。下一轮不应继续单纯增加 route-risk samples 或提高权重；更合理的方向是 soft/top-k target supervision、per-state action constraint，或在 teacher objective 中惩罚 wallward route recovery 的同时保留动作多样性。

## 输出文件

- `low_weight_1_0/opening_training.json`
- `low_weight_1_0/opening.pt`
- `low_weight_1_0/packaging.json`
- `low_weight_1_0/staged.pt`
- `low_weight_1_0/high_pressure_60s_comparison.json`
