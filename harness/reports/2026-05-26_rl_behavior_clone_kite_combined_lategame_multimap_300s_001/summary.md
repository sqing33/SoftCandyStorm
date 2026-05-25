# Behavior Clone Combined Lategame 300s Multi-Map

## 目标

验证组合中后期轨迹训练后的 behavior clone 是否修复 300 秒 high-pressure 长局泛化。

## 结果

- 门禁结论：`multimap_comparison_recorded_needs_policy_repair`
- 地图数：3
- 每图 seeds：3
- 平均 policy win rate：0.2222
- 平均 survival：231.3046 秒
- repair maps：`cracked-star-jar`
- failure case：`harness/failed_cases/fail_20260526_021_behavior_clone_combined_cracked_gap.json`

| Map | Win Rate | Survival | Damage Taken | Entropy | Dominant Ratio | Best Rule Win |
|---|---:|---:|---:|---:|---:|---:|
| `soda-creek` | 0.3333 | 183.1219 | 116.8977 | 0.9211 | 0.1871 | 0.333 |
| `caramel-workshop` | 0.3333 | 247.9951 | 116.2989 | 0.8821 | 0.2605 | 0.667 |
| `cracked-star-jar` | 0.0 | 262.7968 | 120.2558 | 0.8858 | 0.2233 | 0.667 |

## 结论

组合中后期轨迹显著改善长局存活和动作分布，但最终图仍为 0% 胜率。该模型不能推进为 RL 测试 Bot；下一步应针对 `cracked-star-jar` 生成更多最终图中后期危险状态样本，或引入序列上下文。
