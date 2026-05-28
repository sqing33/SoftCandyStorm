# Stage 02 Current-failure Fallback Probe

## 结论

- Gate decision: `current_failure_fallback_no_regression_passed_not_acceptance`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_077_stage02_current_failure_fallback_longrun_gap.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验回到 late-retention fallback 的数据底座，不复用上一轮旧 map-specific repair samples，改为混入 path-weighted failed-only trace 新导出的 `825` 条 current-failure route-recovery samples。全局 `edge_recovery_sample_weight` 仍为 `0.25`，`cracked-star-jar` late-survival anchors 从上一轮 `1.4x` 降到 `1.2x`，`caramel-workshop` opening / late repair samples 为 `0.75x`。

结果：同 seed no-regression 通过，但仍不是 acceptance。相对 seed 63100 stage 02 baseline，60 / 180 / 300 秒均无回归，300 秒三图平均存活都提高：`soda-creek +39.0285s`、`caramel-workshop +7.735s`、`cracked-star-jar +20.1075s`，且 `cracked-star-jar` 300 秒胜率保持 `0.3333`。但 `soda-creek` 与 `caramel-workshop` 300 秒胜率仍为 `0.0`，总失败仍有 `8` 个 episode，因此不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `36426` |
| Edge recovery samples | `2693` |
| Edge recovery sample ratio | `7.39%` |
| Edge recovery sample weight | `0.25` |
| Current-failure repair samples | `825` |
| Path-weighted train samples | `3363` |
| Path-weighted train ratio | `11.54%` |
| Cracked late anchor weights | `1.2x` |
| Caramel repair weights | `0.75x` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7683` |

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
| `300s` | None | `0` | average survival improved, but soda/caramel still no wins |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `1`, late `2` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `2` | mid `1`, late `1` |

## 判断

- Current-failure samples improved survival without reintroducing fixed-window regressions; this is the best supervised fallback branch in the current sequence.
- The remaining gap is still long-run win conversion: `soda-creek` and `caramel-workshop` stay at `0.0` win rate over 300 秒.
- Passing `policy_window_regression` here means only no-regression against the supplied seed 63100 baseline. It is not policy acceptance and must not be promoted to `rl_test_bot_candidate`.
- 下一步应 either export another trace from this branch to target remaining late deaths, or switch to closed-loop constrained repair using this checkpoint as diagnostic teacher evidence.

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
