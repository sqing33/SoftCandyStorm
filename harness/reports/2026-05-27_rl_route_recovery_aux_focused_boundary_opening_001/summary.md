# Route Recovery Aux Focused Boundary Opening Smoke

## 结论

- Gate decision: `evaluation_recorded_needs_action_bias_repair`
- Staged model: `harness/reports/2026-05-27_rl_route_recovery_aux_focused_boundary_opening_001/staged.pt`
- 新 opening model: `harness/reports/2026-05-27_rl_route_recovery_aux_focused_boundary_opening_001/opening.pt`
- 沿用 mid / late：`harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt` 和 `late.pt`
- Failure case: `harness/failed_cases/fail_20260527_041_route_recovery_aux_focused_boundary_opening_regression.json`

这次 smoke 只重训 opening 子模型，把 `134` 条 focused boundary samples 加入 phase-aligned KiteBot opening 轨迹，并保留上一轮 entropy retry 的 mid / late 子模型。目的是隔离 focused boundary repair input 对 `0-60s` 的影响。

## Training

opening 训练集共有 `5405` 条样本，其中 `17` 条为 `edge_recovery_supervision_sample`，占 `0.0031`。使用 `edge_recovery_sample_weight = 4.0` 后，加权样本数为 `13`，加权比例 `0.0030`。最终 validation accuracy 为 `0.5948`，validation entropy 为 `1.586288` nats。

## Evaluation

5 秒 `soda-creek` seed `62300` smoke 不再是纯 action `3`：

- action `3`: `102/151`，占 `0.6755`
- action `5`: `49/151`，占 `0.3245`
- normalized action entropy: `0.2868`
- gate decision: `evaluation_recorded_not_policy_gate`

但 60 秒同 seed 评估发生明显回归：

- 终局：`player_health_depleted`
- 存活：`42.3664s`
- damage_taken: `120.2898`
- reward: `-13.9897`
- action `7`: `995/1271`，占 `0.7828`
- normalized action entropy: `0.3043`
- route_recovery reward: `-1.0875`
- gate decision: `evaluation_recorded_needs_action_bias_repair`

## 判断

Focused boundary samples 打破了 5 秒 action `3` 纯塌缩，但没有形成稳定恢复策略；低比例 opening repair input 反而把 60 秒行为推向新的 action `7` dominant bias，并导致更早死亡。该 checkpoint 只能作为 repair regression 证据，不能进入 stage 03、high-pressure 候选或 RL acceptance。

下一步不应简单继续放大同一 focused samples 权重；需要先扩充 `20-60s` 多 seed / 多图边界恢复样本，检查 target action 分布是否过度偏向单一撤离方向，并在训练后直接以 deterministic 60 秒多图 opening gate 作为最小门槛。

## 输出文件

- `opening_training.json`
- `packaging.json`
- `evaluation_5s_soda.json`
- `evaluation_60s_soda.json`
- `online_60s_trace/soda-creek_seed62300_trace.json`
