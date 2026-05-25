# Behavior Clone Combined Lategame 60s Multi-Map

## 目标

验证组合中后期轨迹训练后的 behavior clone 是否保留 60 秒 high-pressure 稳定性。

## 结果

- 门禁结论：`multimap_comparison_recorded_not_balance_gate`
- 地图数：3
- 每图 seeds：5
- 平均 policy win rate：1.0
- repair maps：0

| Map | Win Rate | Survival | Damage Taken | Entropy | Dominant Ratio |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 10.3720 | 0.8766 | 0.2433 |
| `caramel-workshop` | 1.0 | 60.0328 | 18.7400 | 0.8783 | 0.2105 |
| `cracked-star-jar` | 1.0 | 60.0328 | 25.6120 | 0.8687 | 0.3045 |

## 结论

60 秒短中局明显优于上一版 expanded BC，动作分布也更健康。仍需 300 秒长局验证。
