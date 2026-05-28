# Stage 02 Staged Fallback Late Retention Probe

## 结论

- Gate decision: `staged_fallback_late_retention_no_regression_passed_not_acceptance`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_073_stage02_staged_fallback_late_retention_longrun_gap.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验在上一轮低权重 route-recovery fallback repair 的基础上，额外混入真实 `180-300s` late-survival rule Bot trajectories，并把 edge recovery repair rows 权重降到 `0.25`。目标是保护 `cracked-star-jar` late retention，避免上一轮 behavior-clone fallback 把 300 秒 cracked 胜率从 `0.3333` 拉回 `0.0`。

结果：同 seed no-regression 通过，但仍不是 acceptance。60 / 180 / 300 秒相对 seed 63100 stage 02 baseline 全部无回归，`cracked-star-jar` 300 秒胜率保持 `0.3333`，平均存活高于 baseline `9.0849s`；但 `soda-creek` 和 `caramel-workshop` 300 秒胜率仍为 `0.0`，总计仍有 `8` 个失败 episode。

## Training

| Item | Value |
| --- | --- |
| Samples | `35601` |
| Edge recovery samples | `1868` |
| Edge recovery sample ratio | `5.25%` |
| Late phase ratio | `52.89%` |
| Edge recovery sample weight | `0.25` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7657` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Seed 63100 Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening preserved |
| `180s` | None | `0` | no fixed-window regression |
| `300s` | None | `0` | cracked preserved, soda/caramel still not solved |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `2`, late `1` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `2` | mid `1`, late `1` |

## 判断

- Adding real late-survival trajectories is useful: it restores `cracked-star-jar` 300 秒 behavior without reintroducing fixed-window regression.
- The remaining blocker has moved to map-specific recovery: `soda-creek` mid-window and `caramel-workshop` opening / late recovery.
- This checkpoint can be used as a diagnostic branch for the next probe, but it is still `not_acceptance` and must not be promoted to `rl_test_bot_candidate`.

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
