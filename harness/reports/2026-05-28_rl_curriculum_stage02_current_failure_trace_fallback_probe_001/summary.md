# Stage 02 Current-failure Trace Fallback Probe

## 结论

- Gate decision: `current_failure_trace_fallback_previous_best_regression`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_078_stage02_current_failure_trace_fallback_previous_best_regression.json`
- Baseline no-regression report: `window_regression_vs_seed63100_stage02.md`
- Previous-best regression report: `window_regression_vs_current_failure_best.md`

本实验回到 current-failure fallback 的 late-retention 数据底座，但把上一轮 path-weighted trace 的 `825` 条 repair samples 替换为 current-failure trace 新导出的 `772` 条更窄 map/time-window samples。全局 `edge_recovery_sample_weight` 仍为 `0.25`，`cracked-star-jar` late-survival anchors 保持 `1.2x`，`soda-creek` / `caramel-workshop` opening samples 与 `caramel-workshop` late samples 使用 `0.75x`。

结果：相对 seed 63100 stage 02 baseline 的 60 / 180 / 300 秒同 seed no-regression 通过，但相对上一版 current-failure fallback best 明显回归。300 秒三图胜率全部为 `0.0`，`cracked-star-jar` 丢掉上一版 `0.3333` 胜率；对 previous-best 的 window regression 有 6 个 blockers。因此该 checkpoint 不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance，也不应替代上一版 current-failure fallback best。

## Training

| Item | Value |
| --- | --- |
| Samples | `36373` |
| Edge recovery samples | `2640` |
| Edge recovery sample ratio | `7.26%` |
| Edge recovery sample weight | `0.25` |
| Current-failure trace samples | `772` |
| Path-weighted train samples | `3283` |
| Path-weighted train ratio | `11.28%` |
| Cracked late anchor weights | `1.2x` |
| Opening / caramel late repair weights | `0.75x` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7693` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression

Against seed 63100 stage 02 baseline:

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening preserved |
| `180s` | None | `0` | baseline no-regression passed |
| `300s` | None | `0` | average survival still above baseline, but no wins |

Against previous current-failure fallback best:

| Window | Regressed maps | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening unchanged |
| `180s` | `soda-creek`, `cracked-star-jar` | `2` | average survival dropped |
| `300s` | `soda-creek`, `caramel-workshop`, `cracked-star-jar` | `4` | cracked win lost and average survival dropped |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `2`, late `1` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `3` | mid `1`, late `2` |

## 判断

- The narrower current-failure trace sample pack is valid training material, but replacing the prior sample pack lost previous-best retention.
- Passing `window_regression_vs_seed63100_stage02` only means the branch did not fall below the older stage 02 baseline. It is weaker than the previous current-failure fallback best.
- The previous-best regression report is the decisive gate for this probe: the candidate must remain blocked.
- 下一轮应 restore previous-best retention and test current-failure trace samples incrementally, instead of replacing the previous sample pack wholesale.

## 输出文件

- `fallback_training.json`
- `fallback.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `window_regression_vs_current_failure_best.json`
- `window_regression_vs_current_failure_best.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
