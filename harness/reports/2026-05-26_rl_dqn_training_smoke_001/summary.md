# DQN 训练冒烟报告

- 算法：`dqn`
- 阶段：`rl_phase_1_movement_survival`
- 请求训练步数：`128`
- 实际训练步数：`128`
- 评估局数：`2`
- 单局评估时长：`5` 秒
- 内容包：`content/base_demo`
- 模型产物：`python/train/models/dqn_phase1_movement_survival.zip`
- Metadata：`python/train/models/dqn_model_metadata.json`
- 训练报告：`harness/reports/local_rl_training/dqn_training_report.json`
- 评估报告：`harness/reports/local_rl_training/dqn_evaluation_report.json`
- 已知 exploit 记录：`harness/reports/local_rl_training/dqn_known_exploits.json`

## 执行命令

```bash
uv run --with 'gymnasium>=1.0,<2' --with 'numpy>=1.26' --with 'stable-baselines3>=2.0,<3' python python/train/train_sb3.py --algorithm dqn --timesteps 128 --eval-episodes 2 --eval-seconds 5 --report harness/reports/2026-05-26_rl_dqn_training_smoke_001/dqn_training_smoke.json
```

## 结果

- 训练状态：`trained`
- 依赖状态：临时 `uv` 环境内 `gymnasium`、`numpy`、`stable_baselines3` 均可用。
- 评估胜率：`100%`
- 平均存活：`5.0333` 秒
- 平均等级：`1.0`
- 平均击杀：`3.0`
- 平均承伤：`0.0`
- 动作分布：动作 `5` 占比 `93.05%`，动作 `0` 占比 `6.95%`
- 动作熵：`0.3641` bits
- 归一化动作熵：`0.1149`
- 已知 exploit：`dominant_action_bias`、`low_action_entropy`、`terminal_reward_dominance`
- 平均奖励拆解：`terminal=5.0`，`kill=0.15`，`survival=0.0503`，`xp=0.04`
- Gate 结论：`trained_needs_action_bias_repair`

## 限制

- 这次训练只证明 Stable-Baselines3 到 `game_harness gym-bridge` 的真实训练、模型保存和报告写盘链路可用。
- 5 秒、2 局评估不能证明策略有效，也不能作为乐趣、平衡或内容通过门禁。
- 系统 Python 仍缺少训练依赖；本次使用 `uv run --with ...` 创建临时依赖环境完成。
- 后续必须先修复动作塌缩和短局终局奖励主导问题，再进行同 seed / 同 map 规则 Bot 对比。
