# Behavior Clone Kite High-Pressure Smoke

## 目标

验证规则 Bot 轨迹 JSONL 可以被 Python 侧行为克隆入口读取、训练、保存模型并写出报告。

## 数据集

- 来源：`harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001/`
- Bot：`kite`
- 地图：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- 样本：900 条 movement sample
- Episode：6 局
- Observation：v2，长度 145
- Action：9 个离散 movement action
- 跳过升级样本：0

动作分布显示 action `3` 占 50.67%，因此该小样本只适合入口 smoke，不适合直接作为稳定策略质量判断。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001 \
  --epochs 2 \
  --batch-size 128 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_high_pressure_smoke_001/run_output.json
```

## 结果

- 状态：`trained`
- 门禁结论：`behavior_clone_smoke_only_not_policy_gate`
- 模型：`python/train/models/behavior_clone_kite_high_pressure_smoke.pt`
- 训练样本：720
- 验证样本：180
- 第 2 epoch train accuracy：0.5069
- 第 2 epoch validation accuracy：0.5056
- 第 2 epoch validation loss：1.906723

## 限制

- 行为克隆只模仿规则 Bot movement，不是平衡门禁。
- 当前数据跳过升级选择，保持 Phase 1 movement-only action space。
- 模型还没有接入 Gym evaluation，不能作为 RL 测试 Bot 候选。
- 下一步应实现 behavior clone evaluation wrapper，并复用规则 Bot 对比和 action entropy 诊断。
