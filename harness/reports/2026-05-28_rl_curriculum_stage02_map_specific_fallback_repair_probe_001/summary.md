# Stage 02 Map-specific Fallback Repair Probe

## 结论

- Gate decision: `map_specific_fallback_repair_probe_rejected_window_regression`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_074_stage02_map_specific_fallback_repair_probe_window_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验沿用 late-retention fallback 的数据组合，并额外混入当前失败面导出的三包 map-specific route recovery samples：`soda-creek 60-180s`、`caramel-workshop <60s`、`caramel-workshop 180-300s`。为避免再次破坏 `cracked-star-jar` late retention，edge repair rows 只从 `0.25` 小幅提高到 `0.35`。

结果：该 probe 被拒绝。它把 `cracked-star-jar` 300 秒胜率从上一轮 `0.3333` 提到 `0.6667`，总失败数从 `8` 降到 `7`；但 strict no-regression 对 `soda-creek 300s` 记录 `0.0111s` 平均存活回退，且 `soda-creek` / `caramel-workshop` 300 秒胜率仍为 `0.0`。因此不能推进 stage 03 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `35864` |
| Edge recovery samples | `2131` |
| New map-specific samples | `263` |
| Edge recovery sample weight | `0.35` |
| Edge recovery weighted sample ratio | `5.94%` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7644` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.6667` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Seed 63100 Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening preserved |
| `180s` | None | `0` | no fixed-window regression |
| `300s` | `soda-creek` | `1` | strict average survival regression of `0.0111s` |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `2`, late `1` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `1` | mid `1` |

## 判断

- Map-specific samples helped `cracked-star-jar` long-window retention, but did not solve `soda-creek` mid recovery or `caramel-workshop` opening / late recovery.
- Raising the shared edge repair weight to `0.35` is still too blunt: it improves one map while producing a strict `soda-creek` no-regression blocker.
- The next probe should either lower / split map-specific sample weights or move back to closed-loop constraints. This checkpoint is repair evidence only and must not be promoted to `rl_test_bot_candidate`.

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
