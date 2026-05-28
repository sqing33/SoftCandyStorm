# Stage 02 Path-weighted Fallback Probe

## 结论

- Gate decision: `path_weighted_fallback_probe_rejected_window_regression`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_076_stage02_path_weighted_fallback_probe_window_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验使用 `train_behavior_clone.py --sample-path-weight` 拆分样本权重：全局 `edge_recovery_sample_weight` 保持 `0.25`，对 `cracked-star-jar` 的两包 late-survival anchors 施加 `1.4x`，对 `caramel-workshop` opening / late map-specific repair samples 施加 `0.75x`。目标是验证路径级调权能否同时保住 `cracked-star-jar` late retention，并避免上一轮全局权重在 `soda-creek` 与 `cracked-star-jar` 之间摇摆。

结果：该 probe 被拒绝。`cracked-star-jar` 300 秒胜率保住 `0.3333`，且 `caramel-workshop` 300 秒平均存活高于 seed 63100 stage 02 baseline；但 strict no-regression 仍记录 2 个 blocker：`cracked-star-jar` 180 秒平均存活回退 `9.1443s`，`soda-creek` 300 秒平均存活回退 `2.2886s`。`soda-creek` / `caramel-workshop` 300 秒胜率仍为 `0.0`，因此不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `35864` |
| Edge recovery samples | `2131` |
| Edge recovery sample weight | `0.25` |
| Path-weighted train samples | `3196` |
| Path-weighted train ratio | `11.14%` |
| Cracked late anchor weights | `1.4x` |
| Caramel map-specific repair weights | `0.75x` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7612` |

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
| `180s` | `cracked-star-jar` | `1` | average survival regression `9.1443s` |
| `300s` | `soda-creek` | `1` | average survival regression `2.2886s` |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `2`, late `1` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `2` | mid `1`, late `1` |

## 判断

- Path-level weighting is useful as a diagnostic knob, but this weighting recipe still cannot satisfy strict same-seed no-regression.
- Boosting cracked late anchors recovered the 300 秒 cracked win signal, but introduced an 180 秒 cracked survival blocker and did not solve `soda-creek` long-window survival.
- Lowering caramel map-specific repair samples to `0.75x` did not remove the caramel opening / late failure pattern.
- This checkpoint is repair evidence only and must not be promoted to `rl_test_bot_candidate`.

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
