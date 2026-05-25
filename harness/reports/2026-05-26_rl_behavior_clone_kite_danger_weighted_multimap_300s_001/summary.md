# Behavior Clone Danger-Weighted 300s Multi-Map

## 目标

验证危险状态重采样 behavior clone 是否修复 300 秒 high-pressure 长局泛化，并确认它能否推进为 RL 测试 Bot 候选。

## 结果

- 门禁结论：`multimap_comparison_recorded_watch`
- 地图数：3
- 每图 seeds：3
- 平均 policy win rate：0.5556
- 平均 survival：267.7059 秒
- repair maps：无
- watch finding：`cracked-star-jar` policy 胜率低于最强规则 Bot 的一半
- failure case：`harness/failed_cases/fail_20260526_023_behavior_clone_danger_weighted_cracked_watch.json`

| Map | Win Rate | Survival | Damage Taken | Entropy | Dominant Ratio | Best Rule Win |
|---|---:|---:|---:|---:|---:|---:|
| `soda-creek` | 0.6667 | 277.0835 | 82.7489 | 0.9053 | 0.2285 | 0.667 |
| `caramel-workshop` | 0.6667 | 279.4729 | 86.2944 | 0.9239 | 0.2050 | 0.667 |
| `cracked-star-jar` | 0.3333 | 246.5614 | 92.4313 | 0.9030 | 0.2406 | 1.0 |

## 结论

危险状态重采样比单图补强更稳：`soda-creek` 不再 0% 回归，三图动作熵都保持健康。但 `cracked-star-jar` 仍明显低于 KiteBot 规则基线，长局结论只能记为 watch，不能推进为 RL 测试 Bot。下一步应做序列上下文或分阶段 policy，而不是继续单纯追加单图样本。
