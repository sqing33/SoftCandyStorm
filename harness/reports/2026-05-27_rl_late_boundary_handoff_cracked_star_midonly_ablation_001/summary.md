# Cracked Star Handoff Mid-only Ablation

## 结论

- Gate decision: `cracked_star_handoff_midonly_ablation_recorded_needs_policy_repair`
- Variant: `cracked_star_mid_w0_5`
- Sample source: `harness/reports/2026-05-27_rl_late_boundary_handoff_cracked_star_samples_001/cracked_star_handoff_60_90_recovery_samples.jsonl`
- New mid: `cracked_star_mid_w0_5/mid.pt`
- Staged fallback: `cracked_star_mid_w0_5/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_060_late_boundary_handoff_cracked_star_midonly_gap.json`

本轮把 `190` 条 `cracked-star-jar` 专项 `60-90s` handoff route-recovery 样本，与三图 phase-aligned KiteBot 轨迹混合训练 mid-only 小权重消融；配置沿用 `gru context8`、`map-conditioning=one_hot`、`time-phase-conditioning=one_hot`、`time-phase-filter=mid`、`edge_recovery_sample_weight=0.5`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02` 和 `action_distribution_regularization=0.2 / per_map_uniform_present`。随后保留既有 opening / late 子模型打包 staged fallback，并接入 stage01 opening wrapper 做 60 / 180 / 300 秒 high-pressure 三图对比。

结果仍为 repair：60 秒保持 `1.0/1.0/0.8`，180 秒为 `0.6/1.0/0.6`，300 秒三图全为 `0.0`。相较上一轮 60-90 全图样本消融，`cracked-star-jar` 180 秒从 `0.4` 回到 `0.6`，300 秒平均存活也从约 `127.9s` 提高到 `174.6s`；但它没有产生 300 秒胜局，并且 `soda-creek` / `caramel-workshop` 300 秒同样全失败。因此不能推进 stage 03、RL acceptance、playtest 或 release。

## Training

| Samples | Edge samples | Validation accuracy | Validation entropy |
| ---: | ---: | ---: | ---: |
| `10101` | `190` | `0.6589` | `1.180527` |

专项样本在训练集中占比约 `1.88%`，实际 weighted sample count 为 `159`。这说明本轮主要是 map-specific hint，不是新的泛化 fallback policy。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s wrapper` | `1.0` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s wrapper` | `0.6` | `1.0` | `0.6` | `multimap_comparison_recorded_not_balance_gate` |
| `300s wrapper` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `119.2836s` | mid `4`, late `1` | action `7` `51.60%` | `0.6513` |
| `caramel-workshop` | `0.0` | `215.3704s` | late `5` | action `7` `54.39%` | `0.6740` |
| `cracked-star-jar` | `0.0` | `174.6401s` | mid `3`, late `2` | action `7` `39.24%` | `0.8054` |

失败分析共记录 `15` 个死亡局，且 opening bucket 为 `0`。专项样本能把 `cracked-star-jar` 的部分死亡推迟到 late window，但没有解除 300 秒长窗 blocker；同时 `soda-creek` 和 `caramel-workshop` 仍存在 action `7` 主导，说明 map-specific handoff 样本没有形成可靠的跨图 route recovery。

## 下一步

- 不继续只追加 `cracked-star-jar` 同类 60-90 秒 handoff 样本。
- 下一轮应转向 late-window low-health / hazard / Boss pressure recovery，或生成包含 180-300 秒成功/近成功 clean survival 对照的训练输入。
- 任一下一轮候选仍必须保留 60/180/300 秒 deterministic high-pressure 三图门禁，不能用单图改善替代 RL acceptance。

## 输出文件

- `cracked_star_mid_w0_5/mid_training.json`
- `cracked_star_mid_w0_5/mid.pt`
- `cracked_star_mid_w0_5/packaging.json`
- `cracked_star_mid_w0_5/staged.pt`
- `cracked_star_mid_w0_5/high_pressure_60s_wrapper_comparison.json`
- `cracked_star_mid_w0_5/high_pressure_180s_wrapper_comparison.json`
- `cracked_star_mid_w0_5/high_pressure_300s_wrapper_comparison.json`
- `cracked_star_mid_w0_5/failure_analysis_300s.json`
- `cracked_star_mid_w0_5/failure_analysis_300s.md`
