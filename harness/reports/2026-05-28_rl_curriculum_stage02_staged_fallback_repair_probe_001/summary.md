# Stage 02 Staged Fallback Repair Probe

## 结论

- Gate decision: `staged_fallback_repair_probe_rejected_window_regression`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `fallback.pt`
- Failure case: `harness/failed_cases/fail_20260528_072_stage02_staged_fallback_repair_probe_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验训练一个 behavior-clone fallback，不替换 stage 02 opening policy。训练数据以 `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001` 的 phase-aligned 规则轨迹为主体，并低权重混入 staged opening fallback trace 导出的 `60-180s` 与 `180-300s` route-recovery repair samples。Repair rows 共 `1868` 条，占训练数据 `7.92%`。

结果：probe 被拒绝。60 秒三图完全保住，180 / 300 秒同 seed no-regression 只剩 `cracked-star-jar` 平均存活 2 个 blockers；但 300 秒三图胜率仍全为 `0.0`，并把上一轮 staged opening probe 在 `cracked-star-jar` 的 300 秒 `0.3333` 胜率回退为 `0.0`。该模型不能推进 stage 03 或 RL acceptance。

## Training

| Item | Value |
| --- | --- |
| Samples | `23594` |
| Edge recovery samples | `1868` |
| Edge recovery sample weight | `0.5` |
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time-phase conditioning | `one_hot` |
| Epochs | `5` |
| Final validation accuracy | `0.7546` |
| Final validation entropy | `0.981697` |

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
| `180s` | `cracked-star-jar` | `1` | cracked survival regression |
| `300s` | `cracked-star-jar` | `1` | cracked long-window survival regression |

## 判断

- Low-weight repair rows can preserve 60 秒 opening and reduce action dominance, but they do not solve 300 秒 long-run survival.
- Supervised fallback replacement is still weaker than the previous staged opening wrapper because it loses the `cracked-star-jar` 300 秒 win.
- Next work should not simply increase repair-sample weight; it should add explicit `cracked-star-jar` late retention, stronger closed-loop constraints, or return to PPO reward/curriculum repair.

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
