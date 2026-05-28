# Stage 02 Handoff Splice Late Low Weight Probe

## 结论

- Decision: `handoff_splice_late_low_weight_probe_rejected_not_policy_gate`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Added repair input: `harness/reports/2026-05-28_rl_curriculum_stage02_handoff_splice_late_trace_001/late_route_recovery_samples.jsonl`
- Failure case: `harness/failed_cases/fail_20260528_087_stage02_handoff_splice_late_low_weight_regression.json`

本 probe 沿用 current-failure fallback best 的数据底座和训练参数，只额外混入 handoff splice late trace 导出的 `207` 条 `180-300s` route-recovery repair samples，并把该路径权重设为 `0.2x`。目标是验证这批 late repair samples 能否作为低权重增量修复输入，同时保持 current-failure best 的 60 / 180 / 300 秒 retention。

结果：该分支被拒绝。60 秒窗口保持 `1.0/0.6667/1.0`，180 秒为 `0.6667/0.6667/0.6667`，但 300 秒三图仍为 `0.0/0.0/0.0`。相对 current-failure fallback best 有 `5` 个 no-regression blockers，并丢掉 `cracked-star-jar` 300 秒 `0.3333` 胜率；相对 seed63100 stage 02 baseline 仍有 `2` 个 blockers。该结果不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `36633` |
| Edge recovery samples | `2900` |
| Added handoff splice late samples | `207` |
| Handoff splice late train matches | `168` |
| Handoff splice late path weight | `0.2x` |
| Edge recovery sample weight | `0.25` |
| Cracked late anchor weights | `1.2x` |
| Caramel repair weights | `0.75x` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7659` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression

| Baseline | Decision | Blockers | Main regression |
| --- | --- | ---: | --- |
| current-failure fallback best | `policy_window_regression_failed` | `5` | `cracked-star-jar` 300 秒胜率从 `0.3333` 降到 `0.0`，并出现多图 300 秒 survival 回退 |
| seed63100 stage 02 baseline | `policy_window_regression_failed` | `2` | `cracked-star-jar` 180 / 300 秒 survival 回退 |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `3` | mid `1`, late `2` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `3` | mid `1`, late `2` |

## 判断

- Low-weight late route-recovery samples are valid repair material, but they still disturb current-failure best retention.
- The probe improves `soda-creek` 180 秒 win rate on this seed window, but that local gain is outweighed by 300 秒 regressions and loss of the existing `cracked-star-jar` 300 秒 win.
- Do not continue supervised sample stacking from this branch as a policy candidate path. The next repair should switch to closed-loop constrained repair or a stricter per-map late objective with current-failure best as an explicit hard anchor.

## 输出文件

- `fallback_training.json`
- `fallback.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_current_failure_best.json`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
