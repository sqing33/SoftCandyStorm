# Behavior Clone Expanded Training Smoke

## 目标

使用 expanded high-pressure KiteBot 轨迹训练 behavior clone，验证数据覆盖扩展是否能减少 deterministic 单动作塌缩。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --epochs 20 \
  --batch-size 256 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_expanded_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_expanded_smoke_001/run_output.json
```

## 结果

- 状态：`trained`
- class weighting：`none`
- 训练样本：4250
- 验证样本：1062
- 第 20 epoch train accuracy：0.8948
- 第 20 epoch validation accuracy：0.8927
- 第 20 epoch validation loss：0.457147

## 结论

离线准确率低于 weighted 小样本，但后续 Gym 对比显示动作分布明显更健康。该结果支持优先扩大轨迹覆盖，而不是继续只调 loss 权重。
