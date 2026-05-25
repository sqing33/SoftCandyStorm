# PPO 训练冒烟报告

- 算法：`ppo`
- 阶段：`rl_phase_1_movement_survival`
- 请求训练步数：`128`
- 实际训练步数：`256`
- 评估局数：`2`
- 单局评估时长：`5` 秒
- 内容包：`content/base_demo`
- 模型产物：`python/train/models/ppo_phase1_movement_survival.zip`
- Metadata：`python/train/models/ppo_model_metadata.json`
- 训练报告：`harness/reports/local_rl_training/ppo_training_report.json`
- 评估报告：`harness/reports/local_rl_training/ppo_evaluation_report.json`
- 已知 exploit 记录：`harness/reports/local_rl_training/ppo_known_exploits.json`
- Failure case：`harness/failed_cases/fail_20260526_004_ppo_dominant_action_bias.json`

## 执行命令

```bash
uv run --with 'gymnasium>=1.0,<2' --with 'numpy>=1.26' --with 'stable-baselines3>=2.0,<3' python python/train/train_sb3.py --algorithm ppo --timesteps 128 --eval-episodes 2 --eval-seconds 5 --report harness/reports/2026-05-26_rl_ppo_training_smoke_001/ppo_training_smoke.json
```

## 结果

- 训练状态：`trained`
- 依赖状态：临时 `uv` 环境内 `gymnasium`、`numpy`、`stable_baselines3` 均可用。
- 评估胜率：`100%`
- 平均存活：`5.0333` 秒
- 平均等级：`1.0`
- 平均击杀：`2.5`
- 平均承伤：`0.0`
- 动作分布：动作 `7` 占比 `100%`
- 动作熵：`0.0` bits
- 归一化动作熵：`0.0`
- 平均奖励拆解：`terminal=5.0`，`kill=0.125`，`survival=0.0503`，`xp=0.02`
- Gate 结论：`trained_needs_rule_bot_comparison`

## 限制

- 这次训练只证明 PPO 也能通过 Stable-Baselines3 到 `game_harness gym-bridge` 的训练、模型保存和报告写盘链路。
- PPO 与 DQN 一样在短 smoke 中出现单动作塌缩，不能作为内容门禁或策略质量证明。
- 后续应先修复短训练奖励和动作熵问题，再扩大评估窗口并与规则 Bot 矩阵对比。
