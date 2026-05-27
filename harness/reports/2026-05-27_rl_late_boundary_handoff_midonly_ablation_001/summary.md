# Late Boundary Handoff Mid-only Ablation

## 结论

- Gate decision: `late_boundary_handoff_midonly_ablation_recorded_needs_longrun_repair`
- Variant: `handoff_mid_w0_5`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- New mid: `handoff_mid_w0_5/mid.pt`
- Base late: `harness/reports/2026-05-27_rl_late_boundary_lateonly_ablation_001/late_boundary_w0_5/late.pt`
- Failure case: `harness/failed_cases/fail_20260527_056_late_boundary_handoff_midonly_ablation_gap.json`

本轮使用 `harness/reports/2026-05-27_rl_late_boundary_handoff_samples_001/handoff_recovery_samples.jsonl` 做 mid-only 小权重消融。训练只替换 staged behavior clone 的 mid 子模型，保留 `opening_action3_w0_5_windowed` opening 子模型和上一轮 `late_boundary_w0_5` late 子模型；配置使用 `edge_recovery_sample_weight=0.5`、`edge_recovery_min_seconds=60`、`edge_recovery_max_seconds=180`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02`、`action_distribution_regularization=0.2 / per_map_uniform_present`，并取消 class weighting。

结果仍为 repair：60 秒 high-pressure 三图为 `0.4/1.0/0.8`，180 秒为 `0.6/1.0/0.8`，300 秒为 `0.0/0.0/0.4`。该结果没有优于上一轮 late-only 消融，不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Phase | Samples | Edge samples | Validation accuracy | Validation entropy |
| --- | ---: | ---: | ---: | ---: |
| `mid` | `12691` | `2780` | `0.6608` | `1.164734` |

`mid` 数据混合三图 phase-aligned KiteBot 轨迹、既有 route recovery 样本和新导出的 handoff recovery 样本。全部样本落在 `60-180s` mid phase；新 handoff 样本占 `21.91%`，soft target 覆盖 `2780` 条样本，平均非零动作数为 `1.3303`。离线 validation accuracy 可用，但它只证明监督训练链路完成，不代表在线策略通过。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.4` | `multimap_comparison_recorded_needs_policy_repair` |

本轮没有改善 300 秒长窗，也没有修复 `soda-creek` 60 秒短窗缺口。相较上一轮 late-only 消融，胜率矩阵基本不变，但 300 秒 dominant action 回到 action `3`，说明替换 mid 子模型会影响后续 staged policy 的在线分布，却没有形成稳定的 handoff / late recovery 能力。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `143.5903s` | opening `2`, late `3` | action `3` `0.3821` | `0.7164` |
| `caramel-workshop` | `0.0` | `220.9716s` | late `5` | action `3` `0.3587` | `0.7161` |
| `cracked-star-jar` | `0.4` | `219.1738s` | opening `1`, late `2` | action `3` `0.3308` | `0.7655` |

失败分析共记录 `13` 个死亡局：`caramel-workshop` 的失败全部在 `180-300s`，`soda-creek` 和 `cracked-star-jar` 同时存在 opening 早死和 late-window 死亡。`mid_60_to_180` 桶没有死亡，但这不能说明 handoff 已解决，因为 300 秒长窗仍在进入 late 后集中崩溃，且短窗仍未通过。

## 下一步

- 不推进该 staged checkpoint 到 stage 03、RL acceptance、playtest 或 release。
- 不继续单纯提高 handoff recovery 样本权重；当前 mid-only 替换没有带来在线收益。
- 下一轮应优先比较 `opening wrapper + fallback-only` 与 `staged mid-only` 的 60 秒交接状态分布，或把 60-180 秒 handoff 样本转成 fallback policy 约束，同时保留 60/180/300 秒 deterministic high-pressure 三图门禁。
- 300 秒长窗仍需要 late-window low-health / hazard / boss pressure recovery，不应被 mid-only 离线 validation accuracy 掩盖。

## 输出文件

- `handoff_mid_w0_5/mid_dry_run.json`
- `handoff_mid_w0_5/mid_training.json`
- `handoff_mid_w0_5/mid.pt`
- `handoff_mid_w0_5/packaging.json`
- `handoff_mid_w0_5/staged.pt`
- `handoff_mid_w0_5/high_pressure_60s_comparison.json`
- `handoff_mid_w0_5/high_pressure_180s_comparison.json`
- `handoff_mid_w0_5/high_pressure_300s_comparison.json`
- `handoff_mid_w0_5/failure_analysis_300s.json`
- `handoff_mid_w0_5/failure_analysis_300s.md`
