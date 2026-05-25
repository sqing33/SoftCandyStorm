# Behavior Clone Expanded Multi-Map Smoke

## 目标

用 high-pressure 三图短窗对比验证 expanded behavior clone 是否修复 deterministic 单动作塌缩。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --compare-map-preset high-pressure \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_expanded_smoke.pt \
  --eval-episodes 2 \
  --eval-seconds 10 \
  --seed-start 30000 \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_expanded_multimap_smoke_001/comparison.json
```

## 结果

- 门禁结论：`multimap_comparison_recorded_not_balance_gate`
- 地图数：3
- 每图 seeds：2
- 每局时长：10 秒
- 平均 policy win rate：1.0
- repair maps：0

| Map | Entropy | Dominant Action | Dominant Ratio | Win Rate |
|---|---:|---:|---:|---:|
| `soda-creek` | 0.6126 | 3 | 0.3200 | 1.0 |
| `caramel-workshop` | 0.4859 | 4 | 0.4450 | 1.0 |
| `cracked-star-jar` | 0.3370 | 5 | 0.6950 | 1.0 |

## 结论

expanded 数据集修复了 10 秒 high-pressure smoke 中的 deterministic 单动作塌缩，但 `cracked-star-jar` 仍接近动作偏置阈值。下一步必须跑 60 秒和 300 秒高压对比，不能把这个短窗结果当作 RL Bot 可用证明。
