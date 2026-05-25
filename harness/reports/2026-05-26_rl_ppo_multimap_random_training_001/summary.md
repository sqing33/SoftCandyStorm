# PPO 随机多地图训练实验 001

日期：2026-05-26

## 目标

在 `cycle` 多地图 PPO 训练出现单动作塌缩后，改用 `--train-map-selection random` 重新训练同一组 6 张 `base_demo` 地图，验证随机地图采样是否能缓解策略塌缩，并判断模型是否可以进入 6 地图 10 seed / 300 秒跨地图对比。

## 训练配置

- Algorithm: `ppo`
- Requested timesteps: 10000
- Actual timesteps: 10240
- Train maps: `frosting-grassland`, `soda-creek`, `cotton-cloud-pasture`, `caramel-workshop`, `jelly-platform`, `cracked-star-jar`
- Map selection: `random`
- Evaluation: 3 seed / 60 秒默认评估

## 结论

Gate 决策：`trained_needs_action_bias_repair`

`random` 地图选择没有修复多地图 PPO 的动作塌缩。训练后评估中动作 7 占 100.00%，归一化动作熵为 0.0。该模型不得进入规则 Bot 对比、跨地图压力测试或内容门禁判断。

## 关键指标

| 指标 | 结果 |
| --- | ---: |
| Win Rate | 100% |
| 平均存活秒数 | 60.0328 |
| 平均等级 | 1.3333 |
| 平均击杀 | 47.0 |
| 平均承伤 | 14.55 |
| 最大动作占比 | 动作 7 = 100.00% |
| 归一化动作熵 | 0.0 |
| Gate | `trained_needs_action_bias_repair` |

## Reward Breakdown

```json
{
  "action_repeat": -1.7407,
  "damage_taken": -1.164,
  "kill": 3.76,
  "level": 0.2667,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 3.4156,
  "xp": 0.6933
}
```

## 失败原因判断

- `random` 多地图采样入口能运行并记录训练地图，但只改变地图选择策略不足以修复 PPO 当前探索不足和单动作偏置。
- 训练后策略依旧能靠固定向左移动拿到 60 秒短评估胜利，说明短评估窗口和当前 reward/gate 组合仍会放过不可用策略的生存假象。
- `action_repeat` 惩罚已经记录到 reward breakdown，但强度不足以阻止多地图训练后的单方向收敛。

## 下一步

1. 暂停继续做多地图 PPO 长评估，先修训练探索和动作偏置。
2. 优先暴露并尝试 PPO `ent_coef` 参数，或增强 `action_repeat` / 边界停留惩罚。
3. 修复后必须先通过动作分布 gate：最大动作占比低于 75%、归一化动作熵高于 0.25，再运行 6 地图 10 seed / 300 秒对比。
