# Late Boundary Late-only Ablation

## 结论

- Gate decision: `late_boundary_lateonly_ablation_recorded_needs_longrun_repair`
- Variant: `late_boundary_w0_5`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- Base mid: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/mid.pt`
- New late: `late_boundary_w0_5/late.pt`
- Failure case: `harness/failed_cases/fail_20260527_053_late_boundary_lateonly_ablation_gap.json`

本轮使用 `harness/reports/2026-05-27_rl_late_route_action4_midlate_late_boundary_samples_001/late_boundary_recovery_samples.jsonl` 做 late-only 小权重消融。训练只替换 staged behavior clone 的 late 子模型，保留 `opening_action3_w0_5_windowed` opening 子模型和 `route_recovery_aux_entropy_retry` mid 子模型；配置继续使用 `edge_recovery_sample_weight=0.5`、`risk_recovery_sample_weight=4.0`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02`、`action_distribution_regularization=0.2 / per_map_uniform_present`，并取消 class weighting。

结果仍为 repair：60 秒短窗未被破坏，180 秒 `soda-creek` 比上一轮 action4 mid/late 消融恢复到 `0.6`，300 秒 `cracked-star-jar` 从 `0.0` 提到 `0.4`；但 300 秒 `soda-creek` 与 `caramel-workshop` 仍为 `0.0`，不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Phase | Samples | Edge samples | Risk samples | Validation accuracy | Validation entropy |
| --- | ---: | ---: | ---: | ---: | ---: |
| `late` | `15051` | `1001` | `780` | `0.5608` | `1.395933` |

`late` 数据混合三图 phase-aligned KiteBot 轨迹、既有 `risk_recovery` 样本和新导出的 `late_boundary_recovery` 样本。新样本全部落在 `180-300s` late phase，并覆盖 action `3/5/7/4/8/6/2` 等多种贴边失败动作；但离线 validation accuracy 明显低于上一轮 action4 late 子模型，说明样本难度和目标分布更复杂。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.4` | `multimap_comparison_recorded_needs_policy_repair` |

相比 action4 mid/late 消融，本轮保住 60 秒短窗，把 180 秒 `soda-creek` 从 `0.4` 拉回 `0.6`，并让 300 秒 `cracked-star-jar` 出现 `0.4` 胜率。但长局 gate 仍失败，且 `soda-creek` / `caramel-workshop` 没有形成 300 秒存活能力。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `156.1263s` | opening `2`, late `3` | action `1` `0.4886` | `0.7313` |
| `caramel-workshop` | `0.0` | `225.9526s` | late `5` | action `1` `0.3555` | `0.7916` |
| `cracked-star-jar` | `0.4` | `222.3408s` | opening `1`, late `2` | action `1` `0.4566` | `0.7293` |

失败分析共记录 `13` 个死亡局：`caramel-workshop` 的失败全部在 `180-300s`，`soda-creek` 与 `cracked-star-jar` 同时暴露 opening 早死和 late survival 缺口。dominant action 转为 action `1`，说明 late boundary 样本把策略推向了新的离边方向，但它没有稳定解决低血量、敌压、hazard / Boss 压力下的长局路线恢复。

## 下一步

- 不推进该 staged checkpoint 到 stage 03、RL acceptance、playtest 或 release。
- 保留这批 late boundary 样本作为有价值的 repair 输入，但不要单纯继续提高权重。
- 下一轮应优先做 closed-loop late boundary escape / low-health survival curriculum，或补充 180-300 秒成功/近成功 clean survival 对照样本，避免只学习局部离边动作。
- 同时需要继续追踪 `soda-creek` 和 `cracked-star-jar` 的 opening death，确保 late 修复不会掩盖短窗回归。

## 输出文件

- `late_boundary_w0_5/late_dry_run.json`
- `late_boundary_w0_5/late_training.json`
- `late_boundary_w0_5/late.pt`
- `late_boundary_w0_5/packaging.json`
- `late_boundary_w0_5/staged.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
