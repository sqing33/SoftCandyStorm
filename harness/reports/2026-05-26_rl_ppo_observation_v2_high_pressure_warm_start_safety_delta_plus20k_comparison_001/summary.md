# PPO Warm Start Safety Delta 高压地图对比 +20k 001

日期：2026-05-26

## 目标

验证 warm-start + `safety_delta` 继续训练模型是否能把短局动作 gate 改善转化为 300 秒高压地图泛化收益。

## 命令要点

- Algorithm：`ppo`
- Model：`python/train/models/ppo_phase1_observation_v2_high_pressure_warm_start_safety_delta_train300_random_ent002_plus20000_eval60.zip`
- Action selection：`deterministic`
- Compare map preset：`high-pressure`
- Maps：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- Seeds：30000-30009
- Evaluation seconds：300
- Rule Bots：`random`、`kite`、`tank`

## 聚合结果

Gate 决策：`multimap_comparison_recorded_watch`

| Map | Policy 胜率 | 平均存活 | 平均承伤 | 最大动作 | 归一化动作熵 | 最佳规则 Bot 胜率 |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| `soda-creek` | 10% | 136.8586s | 116.7360 | 动作 6 = 51.84% | 0.5059 | 50% |
| `caramel-workshop` | 10% | 229.1113s | 115.6220 | 动作 6 = 45.60% | 0.4848 | 40% |
| `cracked-star-jar` | 20% | 223.1529s | 115.7874 | 动作 6 = 51.91% | 0.4819 | 50% |

总体：

- 平均胜率：13.33%
- 最低胜率：10%
- 平均存活：196.3743 秒
- repair maps：无
- watch findings：`soda-creek`、`cracked-star-jar` 低于最强规则 Bot 的一半

## 对照

相对静态 safety reward 的 fail_015，本轮三张图都不再是 0% 泛化退化。相对无 safety_delta 的 fail_014，本轮胜率改善：`caramel-workshop` 从 0% 到 10%，`cracked-star-jar` 从 10% 到 20%；但 `soda-creek` 平均存活从 217.3437 秒降到 136.8586 秒，整体仍未达到可用 RL 测试 Bot 标准。

## 结论

Warm start 是有效方向：它避免了从零 safety_delta 训练的动作塌缩，也让高压地图全部脱离 0% 胜率。但当前模型仍显著落后规则 Bot，尤其 `soda-creek` 和 `cracked-star-jar` 触发 watch。下一步应继续小步 warm-start 或课程训练，并重点修复中后期高压续航，而不是把该模型推进为内容门禁。

## 产物

- Comparison report：`harness/reports/2026-05-26_rl_ppo_observation_v2_high_pressure_warm_start_safety_delta_plus20k_comparison_001/high_pressure_comparison.json`
