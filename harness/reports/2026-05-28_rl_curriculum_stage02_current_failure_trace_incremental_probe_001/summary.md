# Stage 02 Current-failure Trace Incremental Probe

## 结论

- Gate decision: `current_failure_trace_incremental_regression_blocked`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_079_stage02_current_failure_trace_incremental_regression.json`
- Baseline regression report: `window_regression_vs_seed63100_stage02.md`
- Previous-best regression report: `window_regression_vs_current_failure_best.md`

本实验保留上一版 path-weighted trace repair 数据底座，再以目录权重 `0.5x` 增量混入 current-failure trace 新导出的 `772` 条更窄 map/time-window route-recovery samples。全局 `edge_recovery_sample_weight` 仍为 `0.25`，`cracked-star-jar` late-survival anchors 为 `1.2x`，`caramel-workshop` opening / late repair samples 为 `0.75x`。

结果：增量混入没有解除 long-run blocker，也不能替代上一版 current-failure fallback best。60 秒和 180 秒短窗保持可用，但 300 秒仍为 repair：`soda-creek` 从 `0.0` 提到 `0.3333`，`caramel-workshop` 仍为 `0.0`，`cracked-star-jar` 从上一版 best 的 `0.3333` 回退到 `0.0`。相对 seed 63100 stage 02 baseline 还出现 `caramel-workshop` 300 秒平均存活 `-0.4445s` 的 strict no-regression blocker；相对 previous best 有 2 个 blockers。因此该 checkpoint 不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `37198` |
| Edge recovery samples | `3465` |
| Edge recovery sample ratio | `9.32%` |
| Edge recovery sample weight | `0.25` |
| Path-weighted train samples | `3988` |
| Path-weighted train ratio | `13.40%` |
| Current-failure trace path weight | `0.5x` |
| Current-failure matched train samples | `625` |
| Cracked late anchor weights | `1.2x` |
| Opening / caramel late repair weights | `0.75x` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7595` |

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.3333` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression

Against seed 63100 stage 02 baseline:

| Window | Regressed maps | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening preserved |
| `180s` | None | `0` | mid-window improved |
| `300s` | `caramel-workshop` | `1` | average survival dropped `0.4445s` below strict baseline |

Against previous current-failure fallback best:

| Window | Regressed maps | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening unchanged |
| `180s` | None | `0` | mid-window improved |
| `300s` | `caramel-workshop`, `cracked-star-jar` | `2` | caramel survival dropped and cracked 300 秒胜利丢失 |

## Failure Analysis

| Map | 300s failures | Failure buckets |
| --- | ---: | --- |
| `soda-creek` | `2` | mid `1`, late `1` |
| `caramel-workshop` | `3` | opening `1`, late `2` |
| `cracked-star-jar` | `3` | late `3` |

## 判断

- Incremental current-failure trace mixing produces a partial `soda-creek` 300 秒 win signal, but it loses the previous best `cracked-star-jar` 300 秒 win.
- The tiny `caramel-workshop` strict baseline survival regression means this checkpoint is not even clean no-regression evidence against the seed 63100 stage 02 baseline.
- Passing shorter windows does not imply policy acceptance; the decisive 300 秒 comparison remains `needs_policy_repair`.
- 下一步应回到上一版 current-failure fallback best 作为 retention anchor，避免直接替换或简单增量叠加；更合适的方向是 closed-loop constrained repair、per-map late win-conversion objective，或把 current-failure trace 样本仅作为诊断/小权重候选。

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
