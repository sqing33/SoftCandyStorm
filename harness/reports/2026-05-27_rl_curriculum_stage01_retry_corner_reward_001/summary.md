# Stage 01 Retry Corner Reward Diagnostic

## 结论

- 门禁结论：`repair`
- 被审查项：`rl_curriculum_stage01_retry_corner_reward`
- 本次只验证 reward 诊断字段是否覆盖已知坏路径，不代表旧 PPO policy 已修复。

## 命令

```bash
SOFT_CANDY_HARNESS_CMD="target/debug/game_harness gym-bridge" \
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --algorithm ppo \
  --evaluate-model \
  --model harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip \
  --eval-episodes 4 \
  --eval-seconds 60 \
  --seed-start 62406 \
  --map-id soda-creek \
  --trace-dir harness/reports/2026-05-27_rl_curriculum_stage01_retry_corner_reward_001/traces \
  --trace-sample-stride 30 \
  --report harness/reports/2026-05-27_rl_curriculum_stage01_retry_corner_reward_001/evaluation.json
```

## 观察

- 评估窗口：`soda-creek`，seed `62406` 到 `62409`，60 秒。
- 胜率：`50%`，seed `62406` 与 `62409` 仍为 opening defeat。
- 平均 reward breakdown 新增 `corner_action_risk = -0.6767`。
- seed `62406` 采样 trace 中 `corner_action_risk` 负值样本 `11` 个，最终死亡帧为 action `4`，`corner_action_risk = -0.006`。
- seed `62409` 采样 trace 中 `corner_action_risk` 负值样本 `11` 个，最终死亡帧为 action `4`，`corner_action_risk = -0.006`。
- seed `62407` / `62408` 成功局最终 action 为 `7`，最终帧 `corner_action_risk = 0`。

## 审查

- 已通过检查：
  - `GymRewardBreakdown` 输出独立 `corner_action_risk` 字段。
  - 总 reward 纳入该字段。
  - 该字段只在开局、右下角边界敌压、持续 action `4` 时变为负值。
  - 成功局转向 action `7` 后不会继续触发该字段。
- 未通过检查：
  - 旧模型仍在 seed `62406` / `62409` opening 死亡。
  - 本次没有重新训练 policy，因此不能证明 soda opening blocker 已修复。

## 下一步

使用新增 reward 字段从 stage 01 retry checkpoint warm start 重新训练 opening repair，并重新跑 60 秒 high-pressure 10 seed 对比。只有 `soda-creek` 通过同一 seed 窗口且动作分布保持健康后，才能继续 stage 02。
