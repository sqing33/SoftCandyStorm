# Late Boundary Handoff 60-90 Mid-only Ablation

## 结论

- Gate decision: `late_boundary_handoff_60_90_midonly_ablation_recorded_needs_policy_repair`
- Variant: `handoff_60_90_mid_w0_5`
- Sample source: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_obs_samples_001/handoff_60_90_recovery_samples.jsonl`
- New mid: `handoff_60_90_mid_w0_5/mid.pt`
- Staged fallback: `handoff_60_90_mid_w0_5/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_058_late_boundary_handoff_60_90_midonly_tradeoff.json`

本轮只用新导出的 `713` 条 `60-90s` handoff route-recovery 样本，加上三图 phase-aligned KiteBot 轨迹，训练 mid-only 小权重消融；没有混入旧的 `60-180s` handoff 样本或通用 route-recovery 样本。配置沿用 `gru context8`、`map-conditioning=one_hot`、`time-phase-conditioning=one_hot`、`time-phase-filter=mid`、`edge_recovery_sample_weight=0.5`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02` 和 `action_distribution_regularization=0.2 / per_map_uniform_present`。

结果仍为 repair：60 秒 wrapper high-pressure 三图保持 `1.0/1.0/0.8`，但 180 秒为 `0.6/1.0/0.4`，300 秒只有 `0.2/0.2/0.0`。该消融有局部改善，但不是净修复，不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Samples | Edge samples | Validation accuracy | Validation entropy |
| ---: | ---: | ---: | ---: |
| `10624` | `713` | `0.6094` | `1.219960` |

新样本在训练集中占比约 `6.71%`。dry/training 链路能消费样本，但这只证明 supervised plumbing 完成；在线结果仍必须由 high-pressure 比较决定。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s wrapper` | `1.0` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s wrapper` | `0.6` | `1.0` | `0.4` | `multimap_comparison_recorded_watch` |
| `300s wrapper` | `0.2` | `0.2` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

相较上一轮 wrapper probe 的 `180s 0.6/0.6/0.6`、`300s 0.0/0.0/0.0`，本轮把 `caramel-workshop` 180 秒提升到 `1.0`，并让 `soda-creek` / `caramel-workshop` 300 秒各有 `0.2` 胜率；但 `cracked-star-jar` 180 秒降到 `0.4` 且 300 秒仍为 `0.0`。这说明窄 handoff 样本不是可靠的跨图 fallback 修复。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.2` | `152.0257s` | mid `3`, late `1` | action `7` `32.96%` | `0.8341` |
| `caramel-workshop` | `0.2` | `223.8548s` | mid `1`, late `3` | action `7` `33.79%` | `0.8267` |
| `cracked-star-jar` | `0.0` | `127.8633s` | mid `4`, late `1` | action `7` `54.19%` | `0.5954` |

失败分析共记录 `13` 个死亡局，且 opening bucket 为 `0`。死亡仍集中在 handoff/mid 和 late 窗口；`cracked-star-jar` 的 mid-window 死亡最多，是下一轮最明显的回归面。

## 下一步

- 不继续只追加同类 `60-90s` edge 样本或单纯提高其权重。
- 若继续监督修复，应比较 fallback-only 约束与 cracked-star-jar 专项 handoff 样本，而不是只替换 staged mid 子模型。
- 300 秒长窗仍需要 late-window low-health / hazard / Boss pressure recovery；任何下一轮候选仍必须跑 60/180/300 秒 deterministic high-pressure 三图。

## 输出文件

- `handoff_60_90_mid_w0_5/mid_training.json`
- `handoff_60_90_mid_w0_5/mid.pt`
- `handoff_60_90_mid_w0_5/packaging.json`
- `handoff_60_90_mid_w0_5/staged.pt`
- `handoff_60_90_mid_w0_5/high_pressure_60s_wrapper_comparison.json`
- `handoff_60_90_mid_w0_5/high_pressure_180s_wrapper_comparison.json`
- `handoff_60_90_mid_w0_5/high_pressure_300s_wrapper_comparison.json`
- `handoff_60_90_mid_w0_5/failure_analysis_300s.json`
- `handoff_60_90_mid_w0_5/failure_analysis_300s.md`
