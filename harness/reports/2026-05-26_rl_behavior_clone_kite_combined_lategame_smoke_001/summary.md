# Behavior Clone Combined Lategame Training

## 目标

将 0-60 秒 expanded 轨迹与 60-300 秒 lategame 轨迹合并训练，避免只学中后期而丢失开局状态。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --epochs 20 \
  --batch-size 256 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_combined_lategame_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_combined_lategame_smoke_001/run_output.json
```

## 结果

- 状态：`trained`
- 总样本：15102
- Episode：30
- 训练样本：12082
- 验证样本：3020
- 第 20 epoch train accuracy：0.9078
- 第 20 epoch validation accuracy：0.8901
- 第 20 epoch validation loss：0.338143

## 结论

组合数据集保留开局和中后期状态，离线验证稳定。是否可作为候选必须以后续 Gym 60/300 秒对比为准。
