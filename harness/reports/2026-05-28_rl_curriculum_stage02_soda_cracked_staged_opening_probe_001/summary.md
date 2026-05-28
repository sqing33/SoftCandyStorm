# Stage 02 Opening + Soda / Cracked Retention Probe

## 结论

- Gate decision: `staged_opening_no_regression_passed_not_acceptance`
- Opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_cracked_retention_probe_001/ppo_soda_cracked_retention_probe.zip`
- Opening seconds: `60`
- No-regression report: `window_regression_vs_seed63100_stage02.md`
- Failure case: `harness/failed_cases/fail_20260528_071_stage02_soda_cracked_staged_opening_longrun_gap.json`

本实验不训练新 checkpoint，只用 stage 02 PPO 保护前 `60s` opening，再切到 soda/cracked retention checkpoint。目标是验证显式 opening protection 能否消除上一轮 soda seed `63100` 的 opening 回归，并判断 fallback 是否有长窗价值。

结果：同 seed no-regression 通过。相对 `seed_start 63100` stage 02 baseline，60 秒三图完全持平，180 秒三图无回归，300 秒 `cracked-star-jar` 从 `0.0` 提到 `0.3333`，平均存活也提高 `23.7861s`；`soda-creek` 300 秒平均存活提高 `6.6225s`。但该 staged wrapper 仍不是 RL acceptance：300 秒 `soda-creek` 和 `caramel-workshop` 胜率仍为 `0.0`，总计仍有 `8` 个失败 episode。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Seed 63100 Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | None | `0` | opening behavior preserved |
| `180s` | None | `0` | no fixed-window regression |
| `300s` | None | `0` | cracked improves, soda/caramel still not solved |

## 判断

- Explicit opening protection is useful: it removes the soda opening regression introduced by the narrow retention checkpoint.
- The fallback policy has some value in `cracked-star-jar` 300 秒, but does not solve soda/caramel long-run survival.
- Next work should treat staged opening as a diagnostic branch and focus on 60-180 / 180-300 fallback repair, with the same seed-matched no-regression gate.

## 输出文件

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_stage02.json` / `window_regression_vs_stage02.md`（历史跨 seed 诊断，不作为严格 no-regression 结论）
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
