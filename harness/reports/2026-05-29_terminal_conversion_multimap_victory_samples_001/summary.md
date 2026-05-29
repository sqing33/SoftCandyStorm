# 多图终局胜利样本过滤报告

- item_id: `terminal_conversion_multimap_victory_samples`
- gate_decision: `dataset_validated_not_training_gate`
- 结论: `training_input_ready_not_policy_gate`

## 目标

在单图 `cracked-star-jar` 胜利终局样本之外，扩大 terminal-conversion branch 的成功终局正例覆盖。该报告复用 `tools/filter_bot_trajectory_samples.py`，从既有规则 Bot late-survival trajectories 中抽取所有 high-pressure 地图的 victory episode，在 `210-240s` 窗口保留 movement samples。

## 过滤结果

- Source: `harness/reports/2026-05-27_rl_rule_bot_late_survival_trajectory_001`
- Output: `victory_terminal_210_240.jsonl`
- Source episodes: `31`
- Source samples: `12007`
- Kept episodes: `8`
- Kept samples: `1437`
- Terminal distribution: `victory: 8`

按地图分布：

- `soda-creek`: `5` episodes, `899` samples
- `cracked-star-jar`: `2` episodes, `358` samples
- `caramel-workshop`: `1` episode, `180` samples

按 Bot 分布：

- `kite`: `6` episodes
- `greedy`: `1` episode
- `tank`: `1` episode

## Dry Run

`train_behavior_clone.py --dry-run` 已能读取该数据集：

- sample_count: `1437`
- episode_count: `8`
- observation_len: `145`
- action_count: `9`
- time range: `210.0159-239.8556s`
- health_ratio_min: `0.1582`
- health_ratio_average: `0.5282`
- late_low_health_ratio: `0.7543`

诊断 flags：

- `high_action_persistence`: watch，同动作持续率 `0.7668`
- `map_sample_imbalance`: watch，`soda-creek` 样本占比 `0.6256`

## Harness Review

通过：

- 样本来自真实规则 Bot victory trajectories，不是手写 adapter。
- 输出 JSONL 可被 behavior clone 数据加载器读取。
- 三张 high-pressure 地图均有终局正例覆盖。

未通过：

- 该报告没有训练模型。
- 没有 SB3 distillation、anchor alignment、fixed-window comparison、online action-distribution delta、failure analysis 或 repair-probe gate。
- `caramel-workshop` 只有 `1` 个 episode，地图分布仍不均衡。

## Next Step

下一轮 terminal-conversion branch 训练应使用该多图 victory target，并继续混入 parent/e30 retention anchors、mid-anchor drift rows 与 clean risk rows。任何 checkpoint 仍必须通过 full-anchor alignment、60/180/300 秒 high-pressure、多基线 no-regression、online action-distribution delta 和 repair-probe gate。
