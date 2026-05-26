# RL Movement + Upgrade Ranker High-Pressure Compare

## 结论

旧 movement behavior clone 加上多地图升级选择 ranker 后，Gym comparison 仍为 `multimap_comparison_recorded_needs_policy_repair`。升级 ranker 确实被调用，但 movement policy 在 60 秒和 300 秒 high-pressure 三图中都塌缩为 deterministic action `3`，无法推进为 RL 测试 Bot。

对应 failure case：`harness/failed_cases/fail_20260527_014_upgrade_ranker_joint_action_bias.json`。

## 60 秒对比

命令输出：`comparison_60s.json`

| Map | Policy Win Rate | Avg Survival | Upgrade Decisions | Dominant Action | Rule Bot Best |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 38.2442 | 3 | `3` / 100% | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 3 | `3` / 100% | 1.0 |
| `cracked-star-jar` | 0.0 | 29.2110 | 1 | `3` / 100% | 1.0 |

60 秒平均 policy 胜率为 0.4444，三图均因动作分布进入 repair；`cracked-star-jar` 额外触发 0% 胜率 repair。

## 300 秒对比

命令输出：`comparison_300s.json`

| Map | Policy Win Rate | Avg Survival | Upgrade Decisions | Dominant Action | Rule Bot Best |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 33.1332 | 1 | `3` / 100% | 0.333 |
| `caramel-workshop` | 0.0 | 157.2447 | 4 | `3` / 100% | 0.0 |
| `cracked-star-jar` | 0.0 | 42.9108 | 3 | `3` / 100% | 0.667 |

300 秒平均 policy 胜率为 0.0，三图全部同时触发 action distribution repair 和 0% policy win rate repair。

## 判断

- upgrade ranker plumbing 可用，但不是当前主要瓶颈。
- 旧 movement clone 的 deterministic action collapse 仍是首要 blocker。
- 下一步应设计 movement+upgrade 联合 curriculum、阶段目标或重新训练 movement policy，而不是继续扩大升级样本后直接期待长局修复。
