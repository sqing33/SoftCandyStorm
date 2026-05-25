# Behavior Clone Cracked-Augmented 60s Multi-Map

## 目标

验证最终图定向补强后，60 秒 high-pressure 短中局是否保持稳定。

## 结果

- 门禁结论：`multimap_comparison_recorded_not_balance_gate`
- 地图数：3
- 每图 seeds：5
- 平均 policy win rate：1.0
- repair maps：0

| Map | Win Rate | Survival | Damage Taken | Entropy | Dominant Ratio |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 2.9240 | 0.9259 | 0.2212 |
| `caramel-workshop` | 1.0 | 60.0328 | 0.2567 | 0.9060 | 0.2530 |
| `cracked-star-jar` | 1.0 | 60.0328 | 29.5093 | 0.8788 | 0.2973 |

## 结论

60 秒短中局没有回归，问题仍集中在 300 秒长局泛化。
