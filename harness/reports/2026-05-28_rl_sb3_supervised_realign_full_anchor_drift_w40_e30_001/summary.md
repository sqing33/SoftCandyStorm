# SB3 Supervised Re-align Full-anchor Drift W40 E30

## 结论

- Decision: `sb3_supervised_realign_full_anchor_drift_w40_e30_rejected_longrun_gap`
- Anchor drift gate: `behavior_clone_anchor_alignment_within_thresholds`
- Full anchor gate: `behavior_clone_anchor_alignment_within_thresholds`
- 60s gate: `multimap_comparison_recorded_watch`
- 180s gate: `multimap_comparison_recorded_watch`
- 300s gate: `multimap_comparison_recorded_needs_policy_repair`
- Model: `ppo_supervised_realign_full_anchor_drift_w40_e30.zip`
- Teacher fallback: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Teacher opening: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Drift dataset: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/mid_anchor_drift_training_samples.jsonl`
- Failure case: `harness/failed_cases/fail_20260528_093_sb3_supervised_realign_full_anchor_drift_w40_e30_longrun_gap.json`

本次 probe 延续 full-anchor + top drift rows `40x` supervised SB3 PPO 初始化，但把 distillation epochs 从 `5` 提高到 `30`。结果证明上一轮 `w40` 的一部分问题确实是欠拟合：训练报告 final validation argmax accuracy 提升到 `0.797`，drift slice validation argmax accuracy 达到 `0.9556`，full-anchor alignment 也从上一轮失败变为通过。

但该 checkpoint 仍被拒绝。离线 anchor alignment 只说明 policy 没有明显偏离 behavior-clone anchor；固定窗口 high-pressure 对比显示它仍不能把 300 秒长局转换为胜利。`soda-creek`、`caramel-workshop`、`cracked-star-jar` 在 300 秒均为 `0.0` 胜率，gate 输出 `multimap_comparison_recorded_needs_policy_repair`。因此不得进入 guarded PPO、RL acceptance 或 policy candidate。

## Training

| Item | Value |
| --- | --- |
| Samples | `36626` |
| Anchor drift samples | `200` |
| Weighted train drift samples | `155` |
| Drift path weight | `40.0x` |
| Epochs | `30` |
| Batch size | `512` |
| Learning rate | `0.0003` |
| Final train loss | `1.181854` |
| Final validation loss | `1.12848` |
| Final validation argmax accuracy | `0.797` |

## Validation Slices

| Slice | Samples | Loss | Argmax accuracy | Entropy |
| --- | ---: | ---: | ---: | ---: |
| `anchor_drift_diagnostic` | `45` | `1.407348` | `0.9556` | `1.418922` |
| `edge_recovery_supervision` | `554` | `1.688822` | `0.6643` | `1.520232` |
| `trajectory` | `6726` | `1.08046` | `0.8069` | `1.134661` |

## Anchor Alignment

| Scope | Samples | Mean KL | Max KL | Argmax agreement | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Top drift rows | `200` | `0.017394` | `0.444917` | `0.985` | `behavior_clone_anchor_alignment_within_thresholds` |
| Full anchor + drift | `36626` | `0.105281` | `2.503624` | `0.8282` | `behavior_clone_anchor_alignment_within_thresholds` |

full-anchor alignment 的 `opening_lt_60` argmax 仍偏低，后续不能只看 overall 指标；但本次主要 blocker 已从离线 alignment 转移到 300 秒 closed-loop conversion。

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_watch` | `0.3333` | `0.6667` | `0.6667` |
| `180s` | `multimap_comparison_recorded_watch` | `0.3333` | `0.6667` | `0.6667` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.0` |

300 秒平均存活分别为 `149.3442`、`151.8889`、`170.4247`。`failure_analysis_300s.json` 记录 `9` 条失败局，全部为 `player_health_depleted`；每张图各有 `1` 条 opening failure 与 `2` 条 late-window failure，dominant action 都是 action `5`。

## 判断

- `30` epoch supervised re-alignment 解决了上一轮 `5` epoch 欠拟合导致的离线 anchor alignment failure。
- 该 checkpoint 仍缺少 300 秒 long-run route recovery / win conversion 能力，三张 high-pressure 地图全为 `0.0` 胜率。
- 离线 anchor alignment 通过不能替代 fixed-window high-pressure、no-regression 或 RL acceptance。
- 下一步应把问题拆成 closed-loop long-run conversion repair：保留 full-anchor alignment 作为硬 preflight，同时对 300 秒失败局做 per-map late objective 或 online no-regression guard；不要直接从该 checkpoint 推进 policy candidate。

## 输出文件

- `distillation_report.json`
- `ppo_supervised_realign_full_anchor_drift_w40_e30.zip`
- `ppo_supervised_realign_full_anchor_drift_w40_e30_metadata.json`
- `anchor_drift_alignment.json`
- `full_anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
