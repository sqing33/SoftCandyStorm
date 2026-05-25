# Behavior Clone Weighted Training Smoke

## 目标

验证 `--class-weighting inverse_frequency` 是否能缓解小样本 behavior clone 的 majority-action deterministic 塌缩。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001 \
  --epochs 20 \
  --batch-size 128 \
  --class-weighting inverse_frequency \
  --model-out python/train/models/behavior_clone_kite_high_pressure_weighted_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_weighted_smoke_001/run_output.json
```

## 结果

- 状态：`trained`
- class weighting：`inverse_frequency`
- 训练样本：720
- 验证样本：180
- 第 20 epoch train accuracy：0.9486
- 第 20 epoch validation accuracy：0.9222
- 第 20 epoch validation loss：0.501305

## 结论

离线验证准确率提高，但不能说明策略可用。后续 Gym 对比显示 deterministic 策略仍然 100% 塌缩到单一动作，因此本训练只记录为失败修复尝试。
