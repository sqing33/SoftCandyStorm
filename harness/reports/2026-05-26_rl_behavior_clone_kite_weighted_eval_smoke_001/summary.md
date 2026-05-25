# Behavior Clone Weighted Evaluation Smoke

## 目标

验证 inverse-frequency weighted behavior clone 在 Gym 对比中是否修复 deterministic 动作塌缩。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_weighted_smoke.pt \
  --eval-episodes 2 \
  --eval-seconds 10 \
  --seed-start 30000 \
  --map-id soda-creek \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_weighted_eval_smoke_001/comparison.json
```

## 结果

- policy win rate：1.0
- policy average kills：8.0
- normalized action entropy：0.0
- action `5` 占比：100%
- action score diagnostic：`probability`
- 门禁结论：`comparison_recorded_needs_action_bias_repair`
- failure case：`harness/failed_cases/fail_20260526_019_behavior_clone_weighted_action_collapse.json`

## 结论

类别加权没有修复 deterministic 塌缩，只是把塌缩动作从 action `3` 转移到 action `5`。下一步应扩大轨迹数据并改采样/时序建模，不能继续只堆 loss 权重。
