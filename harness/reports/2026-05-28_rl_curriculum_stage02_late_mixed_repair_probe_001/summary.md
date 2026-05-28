# Stage 02 Late Mixed Repair Probe

## 结论

- Gate decision: `late_mixed_repair_probe_rejected_opening_mid_regression`
- Model: `staged.pt`
- Late submodel: `late.pt`
- Failure case: `harness/failed_cases/fail_20260528_067_stage02_late_mixed_repair_probe_regression.json`

本实验把 527 条 late route-recovery repair samples 与三图 clean late survival trajectories 混合训练，repair rows 权重为 `0.5`，并保留既有 opening / mid 子模型打包成 staged behavior clone。该实验是 repair probe，不是 RL acceptance evidence。

结果：probe 仍被拒绝。混入 clean late survival trajectories 后，sample-only probe 的问题没有消失；60 秒仍为 `0.3333/1.0/0.6667`，180 秒变成 `0.0/1.0/0.3333`，300 秒三图全 `0.0`。这说明当前 staged behavior clone late 替换路径仍会造成 phase 行为失稳。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.3333` | `1.0` | `0.6667` | `multimap_comparison_recorded_watch` |
| `180s` | `0.0` | `1.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `3` | soda opening `2`, cracked opening `1` | action `3` early failures |
| `180s` | `5` | soda opening `2` / mid `1`, cracked opening `1` / mid `1` | action `1` mid failures |
| `300s` | `9` | soda opening `2` / mid `1`, caramel late `3`, cracked opening `1` / mid `1` / late `1` | action `1` late/mid failures |

## 判断

- Clean late trajectory mixing did not protect short-window behavior.
- The staged behavior clone replacement path is currently less promising than the stage 02 PPO checkpoint, which at least preserved 60 / 180 秒 before failing 300 秒。
- The next repair should return to closed-loop PPO reward / curriculum shaping, or add explicit phase no-regression constraints before any supervised late replacement is retried.

## 输出文件

- `late_training.json`
- `late.pt`
- `packaging.json`
- `staged.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
