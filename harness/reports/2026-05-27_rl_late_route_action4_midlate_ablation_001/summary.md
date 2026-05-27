# Late Route Action4 Mid/Late Ablation

## 结论

- Gate decision: `midlate_action4_ablation_recorded_needs_longrun_repair`
- Variant: `action4_w0_5`
- Base opening: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/opening.pt`
- New mid: `action4_w0_5/mid.pt`
- New late: `action4_w0_5/late.pt`
- Failure case: `harness/failed_cases/fail_20260527_052_late_route_action4_midlate_ablation_gap.json`

本轮使用 `harness/reports/2026-05-27_rl_late_route_action4_samples_001/mid_late_action4_samples.jsonl` 做小权重 mid/late 消融，只替换 staged behavior clone 的 mid 与 late 子模型，保留上一轮能通过 60 秒 hard gate 的 opening 子模型。训练配置取消 `inverse_frequency` class weighting，使用 `edge_recovery_sample_weight=0.5`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02` 和 `action_distribution_regularization=0.2 / per_map_uniform_present`。

结果仍为 repair：60 秒短窗未被破坏，但 180 秒 `soda-creek` 回落，300 秒三图全部失败，不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Phase | Samples | Edge samples | Risk samples | Validation accuracy | Validation entropy |
| --- | ---: | ---: | ---: | ---: | ---: |
| `mid` | `10461` | `550` | `0` | `0.6759` | `1.276256` |
| `late` | `14098` | `48` | `780` | `0.6227` | `1.363897` |

`mid` 数据包含三图 phase-aligned KiteBot 轨迹、原 `route_recovery` 样本和 action4 样本；phase filter 后有 `550` 条 edge recovery 样本。`late` 数据在 late-only risk recovery 消融的基础上加入 action4 样本；phase filter 后只有 `48` 条 action4 edge recovery 样本，说明该样本包对 late 窗口覆盖偏少。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.4` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

相比上一轮 late-only risk recovery 消融，60 秒结果保持一致，但 180 秒 `soda-creek` 从 `0.6` 回落到 `0.4`，300 秒 `cracked-star-jar` 从 `0.2` 回落到 `0.0`。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `137.6423s` | opening `2`, late `3` | action `3` `0.3091` | `0.7703` |
| `caramel-workshop` | `0.0` | `221.4517s` | late `5` | action `3` `0.3213` | `0.7329` |
| `cracked-star-jar` | `0.0` | `184.4544s` | opening `1`, late `4` | action `5` `0.2634` | `0.8364` |

该结果说明小权重 action4 supervision 没有形成稳定的 300 秒路线恢复能力：动作熵没有塌缩，但失败仍集中在低血量、贴边和 late survival 缺口。单纯继续增加这批 action4 样本权重风险较高，因为它在 180 秒已经让 `soda-creek` 回落，并且 late 窗口只有 `48` 条 action4 样本。

## 下一步

- 不继续放大当前 action4 样本权重。
- 优先扩展 `180-300s` 多图 late action4 / action1 / low-health boundary escape 样本，尤其补 `caramel-workshop` 和 `cracked-star-jar`。
- 或转向 closed-loop late survival / boundary escape curriculum，并保留当前 60 秒 hard gate 和 180 秒 regression。
- 长局通过前不得进入 stage 03、RL policy acceptance 或人工试玩候选。

## 输出文件

- `action4_w0_5/mid_dry_run.json`
- `action4_w0_5/late_dry_run.json`
- `action4_w0_5/mid_training.json`
- `action4_w0_5/late_training.json`
- `action4_w0_5/mid.pt`
- `action4_w0_5/late.pt`
- `action4_w0_5/packaging.json`
- `action4_w0_5/staged.pt`
- `action4_w0_5/high_pressure_60s_comparison.json`
- `action4_w0_5/high_pressure_180s_comparison.json`
- `action4_w0_5/high_pressure_300s_comparison.json`
- `action4_w0_5/failure_analysis_300s.json`
- `action4_w0_5/failure_analysis_300s.md`
