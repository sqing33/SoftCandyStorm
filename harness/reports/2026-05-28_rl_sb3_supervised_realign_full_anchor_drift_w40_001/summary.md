# SB3 Supervised Re-align Full-anchor Drift W40

## 结论

- Decision: `sb3_supervised_realign_full_anchor_drift_w40_rejected_anchor_alignment`
- Gate decision: `behavior_clone_anchor_alignment_failed`
- Model: `ppo_supervised_realign_full_anchor_drift_w40.zip`
- Teacher fallback: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Teacher opening: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Drift dataset: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/mid_anchor_drift_training_samples.jsonl`
- Failure case: `harness/failed_cases/fail_20260528_092_sb3_supervised_realign_full_anchor_drift_w40.json`

本次 probe 使用 full-anchor 数据底座加 top `200` mid-window drift rows 做 supervised SB3 PPO 初始化。drift rows 通过 `--include-anchor-drift-samples` 读入，并用 `--sample-path-weight ...=40` 放大 supervised loss。训练报告记录 `36626` 条样本，其中 `200` 条为 `anchor_drift_sample`，训练集命中 `155` 条 drift rows，权重均值为 `1.206307`。

该路线有局部改善，但仍被拒绝。top drift rows 的 overall mean KL 从旧起点的 `2.26528` 降到 `0.200915`，但 overall argmax agreement 只有 `0.785`，低于 `0.85` 阈值；`caramel-workshop` mean KL 为 `0.28407`，`soda-creek` mean KL 为 `0.376651`，也超过 `0.25` 分桶阈值。

更大的问题是 full-anchor 对齐失败：overall mean KL 为 `0.434754`，argmax agreement 为 `0.6385`，所有地图分桶和时间分桶 mean KL 都超过阈值。说明当前 `40x` drift 权重虽然拉近了 top drift rows，但没有把 SB3 初始化整体蒸馏到 current-failure fallback anchor 附近。

## Training

| Item | Value |
| --- | --- |
| Samples | `36626` |
| Anchor drift samples | `200` |
| Weighted train drift samples | `155` |
| Drift path weight | `40.0x` |
| Epochs | `5` |
| Batch size | `512` |
| Learning rate | `0.0003` |
| Final train loss | `1.506213` |
| Final validation loss | `1.422262` |
| Final validation argmax accuracy | `0.6223` |

## Anchor Alignment

| Scope | Mean KL | Argmax agreement | Decision |
| --- | ---: | ---: | --- |
| Top drift rows | `0.200915` | `0.785` | `behavior_clone_anchor_alignment_failed` |
| Full anchor + drift | `0.434754` | `0.6385` | `behavior_clone_anchor_alignment_failed` |

## 判断

- Weighted supervised distillation is functional and can strongly reduce the top drift-row mean KL.
- A one-pass MlpPolicy supervised initialization with `40x` drift weight is still too far from the staged behavior-clone anchor.
- Do not launch guarded PPO from this checkpoint; it failed full-anchor preflight before any fixed-window no-regression gate.
- 下一步应改进初始化本身：增加 distillation epochs / lower learning rate、加入 validation-weight reporting、尝试 higher-capacity policy 或先做 unweighted full-anchor distillation 再小步 drift fine-tune。

## 输出文件

- `distillation_report.json`
- `ppo_supervised_realign_full_anchor_drift_w40.zip`
- `ppo_supervised_realign_full_anchor_drift_w40_metadata.json`
- `anchor_drift_alignment.json`
- `full_anchor_alignment.json`
