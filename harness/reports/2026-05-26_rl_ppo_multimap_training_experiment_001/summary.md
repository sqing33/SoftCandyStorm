# PPO 多地图训练实验 001

日期：2026-05-26

## 目标

使用新增的 `--train-maps` / `--train-map-selection` 入口，让 PPO 在 6 张 `base_demo` 地图上按 cycle 方式训练，并验证是否能修复上一轮单地图 PPO 的跨地图泛化不足。

## 训练配置

- Algorithm: `ppo`
- Requested timesteps: 10000
- Actual timesteps: 10240
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `cycle`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_action_bias_repair`

本轮多地图训练没有修复 PPO 泛化问题，反而在训练后评估中出现动作塌缩：动作 6 占 100.00%，归一化动作熵为 0.0。该模型不得进入规则 Bot 对比或跨地图压力测试。

## 关键指标

| 指标 | 结果 |
| --- | ---: |
| Win Rate | 100% |
| 平均存活秒数 | 60.0328 |
| 平均击杀 | 48.0 |
| 平均承伤 | 64.55 |
| 最大动作占比 | 动作 6 = 100.00% |
| 归一化动作熵 | 0.0 |
| Gate | `trained_needs_action_bias_repair` |

## Reward Breakdown

```json
{
  "action_repeat": -1.7227,
  "damage_taken": -5.164,
  "kill": 3.84,
  "level": 0.8,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 0.847,
  "xp": 1.4933
}
```

## 失败原因判断

- `cycle` 多地图训练入口能运行并记录训练地图，但 10000 requested timesteps 对 6 地图分布过短。
- 训练后策略仍能靠单方向移动完成 60 秒短评估，说明当前 action_repeat 惩罚不足以约束 PPO 在多地图训练下的塌缩。
- 默认训练后评估仍是短窗口，能暴露动作塌缩，但不能证明跨地图能力。

## 下一步

1. 先修复多地图 PPO 的动作塌缩，再恢复跨地图对比。
2. 可尝试提高 entropy 系数、调整 action_repeat 惩罚、扩大训练步数或使用 `random` 地图选择。
3. 多地图训练模型只有在通过动作分布 gate 后，才允许运行 6 地图 10 seed / 300 秒对比。
