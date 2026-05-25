# Behavior Clone Expanded 60s Multi-Map

## 目标

验证 expanded behavior clone 是否能从 10 秒短窗推进到 60 秒 high-pressure 三图对比。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --compare-map-preset high-pressure \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_expanded_smoke.pt \
  --eval-episodes 5 \
  --eval-seconds 60 \
  --seed-start 32000 \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_expanded_multimap_60s_001/comparison.json
```

## 结果

- 门禁结论：`multimap_comparison_recorded_not_balance_gate`
- 地图数：3
- 每图 seeds：5
- 平均 policy win rate：0.6667
- 平均 survival：55.5951 秒
- repair maps：0

| Map | Win Rate | Survival | Entropy | Dominant Action | Dominant Ratio |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.8 | 56.3928 | 0.6275 | 7 | 0.4836 |
| `caramel-workshop` | 0.6 | 57.5595 | 0.6177 | 7 | 0.5152 |
| `cracked-star-jar` | 0.6 | 52.8329 | 0.6098 | 7 | 0.6081 |

## 结论

60 秒 smoke 仍然可用，但三图 dominant action 都转向 action `7`，需要 300 秒长局验证确认是否是中后期退化前兆。
