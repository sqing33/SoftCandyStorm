# PPO Observation V2 安全塑形高压地图 50k 对比 001

日期：2026-05-26

## 目标

验证加入 `low_health`、`boundary_risk`、`enemy_pressure`、`hazard_risk`、`boss_pressure` 安全塑形后的 high-pressure train300 50k PPO 模型，是否能在三张高压地图 10 seed / 300 秒 deterministic 对比中修复上一轮泛化失败。

## 结论

Gate 决策：`multimap_comparison_recorded_needs_policy_repair`

安全塑形让短局动作分布更分散、短局承伤更低，但 300 秒高压地图泛化更差：三张地图胜率全部为 0%。这说明当前塑形方式过于惩罚“处在危险状态”，没有给 policy 明确的“正在远离危险/降低风险”正反馈。

## 结果摘要

| Map | PPO Win Rate | 平均存活秒数 | 平均承伤 | 平均击杀 | 最大动作占比 | 归一化动作熵 | 规则 Bot 参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| soda-creek | 0% | 59.3745 | 120.2891 | 91.6 | 动作 4 = 36.25% | 0.5989 | Random 0%，Kite 10%，Tank 50% |
| caramel-workshop | 0% | 158.8643 | 120.6541 | 233.0 | 动作 4 = 46.77% | 0.5755 | Random 0%，Kite 40%，Tank 20% |
| cracked-star-jar | 0% | 114.9160 | 120.3168 | 212.1 | 动作 4 = 34.37% | 0.6161 | Random 0%，Kite 40%，Tank 50% |

## 与上一轮对比

上一轮 high-pressure train300 50k 模型：

- `soda-creek`：10% 胜率，平均存活 217.3437 秒。
- `caramel-workshop`：0% 胜率，平均存活 209.3660 秒。
- `cracked-star-jar`：10% 胜率，平均存活 238.4666 秒。

本轮安全塑形后：

- `soda-creek` 回落到 0%，平均存活降到 59.3745 秒。
- `caramel-workshop` 仍为 0%，平均存活降到 158.8643 秒。
- `cracked-star-jar` 回落到 0%，平均存活降到 114.9160 秒。

## 通过项

- 动作分布 gate 通过：所有地图最大动作占比低于 75%。
- 归一化动作熵更高：三张地图均高于 0.57。
- `reward_breakdown_average` 能记录安全塑形字段，报告可解释性提升。

## 失败项

- 三张高压地图胜率全部为 0%。
- 平均承伤都接近死亡阈值，死亡压力没有被解决。
- 安全塑形降低了固定动作偏置，但没有提升长局生存。
- 当前惩罚项更像“坏状态扣分”，缺少“风险正在下降”的方向性奖励。

## Failure Case

- `harness/failed_cases/fail_20260526_015_ppo_safety_reward_overcorrection.json`

## 下一步

1. 不把该 safety train300 50k PPO policy 推进为 RL 压力测试 Bot。
2. 下一步不要继续按当前权重加大惩罚；应改为记录上一帧 safety risk，奖励风险下降、惩罚风险上升。
3. 降低或门控 `boundary_risk`、`low_health` 的持续惩罚，避免 policy 在进入危险后只获得滞后负反馈。
4. 修复后先跑 60 秒短局动作 gate，再跑 high-pressure 10 seed / 300 秒聚合对比。
