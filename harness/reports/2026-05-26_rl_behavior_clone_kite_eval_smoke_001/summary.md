# Behavior Clone Gym Evaluation Smoke

## 目标

验证 behavior clone checkpoint 可以通过 `train_sb3.py --behavior-clone-model` 接入现有 Gym evaluation、动作分布诊断和规则 Bot 对比报告。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --eval-episodes 2 \
  --eval-seconds 10 \
  --seed-start 30000 \
  --map-id soda-creek \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_eval_smoke_001/comparison.json
```

## 结果

- 状态：`compared`
- policy kind：`behavior_clone`
- 地图：`soda-creek`
- Seeds：2
- 时长：10 秒
- policy win rate：1.0
- policy average kills：7.5
- normalized action entropy：0.0
- action `3` 占比：100%
- action score diagnostic：`probability`
- 门禁结论：`comparison_recorded_needs_action_bias_repair`

## Findings

- `small_sample`：少于 10 seeds，仅可作为 smoke。
- `dominant_action_bias`：action `3` 占 100%。
- `low_action_entropy`：动作熵为 0，需要修复。

## 结论

评估 adapter 可用，但当前小样本 behavior clone 不能推进为 RL 测试 Bot。下一步应扩大轨迹数据、控制动作分布偏置，并在多图长局对比前先修复 deterministic 动作塌缩。
