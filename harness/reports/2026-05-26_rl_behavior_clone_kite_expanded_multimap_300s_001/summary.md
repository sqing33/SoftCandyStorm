# Behavior Clone Expanded 300s Multi-Map

## 目标

验证 expanded behavior clone 是否能在 300 秒 high-pressure 三图中保持可用。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --compare-map-preset high-pressure \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_expanded_smoke.pt \
  --eval-episodes 3 \
  --eval-seconds 300 \
  --seed-start 33000 \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_expanded_multimap_300s_001/comparison.json
```

## 结果

- 门禁结论：`multimap_comparison_recorded_needs_policy_repair`
- 地图数：3
- 每图 seeds：3
- 平均 policy win rate：0.0
- 平均 survival：150.2462 秒
- repair maps：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- failure case：`harness/failed_cases/fail_20260526_020_behavior_clone_expanded_long_gap.json`

| Map | Win Rate | Survival | Entropy | Dominant Action | Dominant Ratio |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 70.4770 | 0.7312 | 7 | 0.3941 |
| `caramel-workshop` | 0.0 | 212.5164 | 0.4540 | 7 | 0.5197 |
| `cracked-star-jar` | 0.0 | 167.7451 | 0.4192 | 7 | 0.7519 |

## 结论

expanded behavior clone 不能作为长局 RL Bot 候选。下一步必须生成覆盖 300 秒中后期状态的规则 Bot 轨迹，或加入序列上下文和危险状态重采样。
