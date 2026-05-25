# DQN Policy 可观测性复查

- 算法：`dqn`
- 模型：`python/train/models/dqn_phase1_movement_survival.zip`
- 地图：`frosting-grassland`
- Seeds：`30000`..`30001`
- 单局时长：`5` 秒
- 报告：`harness/reports/2026-05-26_rl_policy_observability_recheck_001/dqn_rule_bot_comparison.json`

## 新增观测字段

- `action_entropy_bits`
- `normalized_action_entropy`
- `reward_breakdown_average`
- 每局 `reward_breakdown`

## 结果

- DQN policy 胜率：`100%`
- 平均存活：`5.0333` 秒
- 平均击杀：`1.5`
- 动作分布：动作 `1` 占比 `100%`
- 动作熵：`0.0` bits
- 归一化动作熵：`0.0`
- 平均奖励拆解：
  - `terminal`: `5.0`
  - `kill`: `0.075`
  - `survival`: `0.0503`
  - `xp`: `0.02`
  - `damage_taken`: `0.0`
  - `level`: `0.0`
  - `total`: `5.1453`

## 结论

- 可观测性链路已补齐，能解释为什么 5 秒 smoke 会掩盖策略塌缩：总奖励几乎完全由 `duration_reached` 终局奖励贡献。
- 这次复查仍确认 `dominant_action_bias` 和 `low_action_entropy`，DQN smoke policy 不能作为内容门禁。
- Gate 结论保持：`comparison_recorded_not_balance_gate`。
