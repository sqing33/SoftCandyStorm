# Stage 02 Map-specific Fallback w0.25 Probe

## 结论

- Gate decision: `map_specific_fallback_w025_probe_rejected_window_regression`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_075_stage02_map_specific_fallback_w025_cracked_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验沿用 map-specific fallback repair 的数据组合，但把 edge repair rows 权重从 `0.35` 降回 `0.25`。目标是确认上一轮 `soda-creek 300s` 的 `0.0111s` strict no-regression blocker 是否来自共享修复权重过高，并检查能否保留 `cracked-star-jar` 300 秒改善。

结果：该 probe 被拒绝。`soda-creek` 300 秒平均存活从上一轮的轻微回归变成高于 baseline `10.4806s`，但 `cracked-star-jar` 180 秒与 300 秒平均存活均出现 strict no-regression blockers，并且 `cracked-star-jar` 300 秒胜率回到 `0.0`。这说明简单降低全局 repair 权重会丢掉 late-retention 收益，不能推进 stage 03 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `35864` |
| Edge recovery samples | `2131` |
| New map-specific samples | `263` |
| Edge recovery sample weight | `0.25` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7666` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Seed 63100 Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening preserved |
| `180s` | `cracked-star-jar` | `1` | average survival regression `5.8s` |
| `300s` | `cracked-star-jar` | `1` | average survival regression `19.3806s` |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `2`, late `1` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `3` | mid `1`, late `2` |

## 判断

- Lowering shared edge repair weight removes the tiny `soda-creek` survival regression, but it also loses `cracked-star-jar` late-retention gains.
- The map-specific samples need more selective weighting or a separate objective; a single global edge recovery weight is not enough.
- This checkpoint is repair regression evidence only and must not be promoted to `rl_test_bot_candidate`.

## 输出文件

- `fallback_dry_run.json`
- `fallback_training.json`
- `fallback.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
