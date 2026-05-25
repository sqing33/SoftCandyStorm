# Behavior Clone Danger-Weighted 60s Multi-Map

## 目标

验证危险状态重采样 behavior clone 在 60 秒 high-pressure 三图短中局中是否保持动作分布健康，并与规则 Bot 基线对比。

## 结果

- 门禁结论：`multimap_comparison_recorded_not_balance_gate`
- 地图数：3
- 每图 seeds：5
- 平均 policy win rate：1.0
- 平均 survival：60.0328 秒
- repair maps：无

| Map | Win Rate | Survival | Damage Taken | Entropy | Dominant Ratio | Best Rule Win |
|---|---:|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 15.6240 | 0.8678 | 0.3301 | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 1.1567 | 0.9107 | 0.2561 | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 3.4853 | 0.9155 | 0.2406 | 1.0 |

## 结论

危险状态重采样通过 60 秒短中局 smoke：三图均 100% 胜率，动作熵健康，最大动作占比不超过 33.01%。该结果只说明短中局没有明显 deterministic collapse，仍不能替代 300 秒长局对比。
