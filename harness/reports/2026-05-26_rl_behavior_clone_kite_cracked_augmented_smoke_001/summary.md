# Behavior Clone Cracked-Augmented Training

## 目标

在 combined lategame 数据基础上追加 `cracked-star-jar` 120-300 秒定向轨迹，尝试修复最终图 300 秒 0% 胜率。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_cracked_lategame_001 \
  --epochs 20 \
  --batch-size 256 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_cracked_augmented_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_cracked_augmented_smoke_001/run_output.json
```

## 结果

- 总样本：19909
- Episode：40
- 训练样本：15927
- 验证样本：3982
- 第 20 epoch train accuracy：0.9190
- 第 20 epoch validation accuracy：0.9098
- 第 20 epoch validation loss：0.272437

## 结论

离线指标继续改善，但是否修复必须以后续 300 秒跨图对比为准。
