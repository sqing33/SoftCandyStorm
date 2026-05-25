# Behavior Clone Cracked-Augmented 300s Multi-Map

## 目标

验证最终图定向补强是否修复 300 秒 high-pressure 长局泛化。

## 结果

- 门禁结论：`multimap_comparison_recorded_needs_policy_repair`
- 平均 policy win rate：0.4445
- 平均 survival：255.6834 秒
- repair maps：`soda-creek`
- failure case：`harness/failed_cases/fail_20260526_022_behavior_clone_cracked_augmented_soda_regression.json`

| Map | Win Rate | Survival | Damage Taken | Entropy | Dominant Ratio | Best Rule Win |
|---|---:|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 220.3292 | 120.7055 | 0.9112 | 0.2156 | 0.333 |
| `caramel-workshop` | 0.6667 | 273.3827 | 82.2389 | 0.9248 | 0.1725 | 0.333 |
| `cracked-star-jar` | 0.6667 | 273.3382 | 93.0933 | 0.8944 | 0.2337 | 0.333 |

## 结论

最终图定向补强成功修复 `cracked-star-jar`，但把失败面移动到 `soda-creek`。下一步应做多图危险状态重采样或序列上下文，不应继续单图加样本。
