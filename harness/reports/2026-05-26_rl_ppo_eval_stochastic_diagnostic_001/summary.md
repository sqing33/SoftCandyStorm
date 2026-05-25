# PPO 随机采样评估诊断 001

日期：2026-05-26

## 目标

复用 `ent_coef=0.02` 的多地图 PPO 模型，在不重新训练的情况下切换为 `--eval-stochastic` 随机采样评估，判断前一轮确定性评估动作 5 占 100% 是策略分布本身完全塌缩，还是确定性 argmax 路径塌缩。

## 评估配置

- Algorithm: `ppo`
- Model: `python/train/models/ppo_phase1_multimap_random_ent002_10000_eval60.zip`
- Map: `frosting-grassland`
- Seed range: `30000-30002`
- Episodes: 3
- Seconds: 60
- Action selection: `stochastic`

## 结论

随机采样评估显示该模型的策略分布仍有动作熵：最大动作为动作 5，占比 33.35%，归一化动作熵为 0.8869。与前一轮确定性评估的动作 5 占 100%、归一化动作熵 0.0 对比，问题更像是确定性 argmax 部署/门禁路径塌缩，而不是训练分布完全死亡。

该结论不解除前一轮 failure case。正式 RL Bot 基线仍应优先使用确定性、可复现策略；随机采样结果只用于诊断 PPO policy 的概率分布和后续训练方向。

## 关键指标

| 指标 | 确定性评估 | 随机采样评估 |
| --- | ---: | ---: |
| Win Rate | 100% | 100% |
| 平均存活秒数 | 60.0328 | 60.0328 |
| 平均等级 | 1.0 | 1.6667 |
| 平均击杀 | 47.0 | 48.0 |
| 平均承伤 | 5.45 | 16.95 |
| 最大动作占比 | 动作 5 = 100.00% | 动作 5 = 33.35% |
| 归一化动作熵 | 0.0 | 0.8869 |

## Reward Breakdown

```json
{
  "action_repeat": 0.0,
  "damage_taken": -1.356,
  "kill": 3.84,
  "level": 0.5333,
  "survival": 0.6003,
  "terminal": 1.0,
  "total": 5.711,
  "xp": 1.0933
}
```

## 判断

- `--eval-stochastic` 入口有效，报告写入 `action_selection: stochastic`。
- PPO policy 的概率分布并非完全单动作，但确定性 argmax 仍不可用。
- 后续若要把 PPO 用作可复现压力测试，应继续修确定性策略；若只是做探索性 exploit 搜索，可以考虑单独定义 stochastic RL Bot，但不能混入确定性门禁。

## 下一步

1. 保留 `fail_20260526_008`，不把该模型推进规则 Bot 对比。
2. 下一轮训练优先增强确定性策略质量，例如提高动作切换/边界惩罚、扩大训练步数，或加入 curriculum。
3. 若继续调 PPO 参数，应同时记录 deterministic 与 stochastic 两套动作分布，避免误判策略是否真正塌缩。
