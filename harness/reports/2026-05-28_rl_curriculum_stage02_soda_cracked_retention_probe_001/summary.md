# Stage 02 Soda / Cracked Retention Probe

## 结论

- Gate decision: `soda_cracked_retention_probe_rejected_opening_regression`
- Model: `ppo_soda_cracked_retention_probe.zip`
- Warm start: `harness/reports/2026-05-28_rl_curriculum_stage02_long_run_retention_probe_001/ppo_long_run_retention_probe.zip`
- Failure case: `harness/failed_cases/fail_20260528_070_stage02_soda_cracked_retention_probe_regression.json`
- No-regression report: `window_regression_vs_seed63100_stage02.md`

本实验从上一轮 `long-run-retention` checkpoint 继续训练，只聚焦 `soda-creek` 和 `cracked-star-jar`，使用 `long-run-retention` reward profile、`4096` timesteps、训练 seed `62800-62802,63100-63102`、learning rate `0.00001`、entropy coefficient `0.03`。目标是验证 map/window-specific retention 是否能修复上一轮 soda/cracked 的 mid/late regression。

结果：probe 被拒绝。补录 `seed_start 63100` stage 02 baseline 后，同 seed no-regression 只剩 `2` 个 blockers，均来自 `soda-creek` 60 秒 opening 回归：胜率从 `1.0` 回到 `0.6667`，平均存活低 `5.8111s`。它修住了 `cracked-star-jar` 180 秒窗口，并让 300 秒三图平均存活都高于 baseline，但 300 秒三图胜率仍全 `0.0`，不能推进 stage 03 或 RL acceptance。

> 注：旧的 `window_regression_vs_stage02.md` 使用 stage 02 `seed_start 62800` baseline 与本 probe 的 `63100` 结果做跨 seed 摘要比较，只保留为历史诊断；严格判断以 `window_regression_vs_seed63100_stage02.md` 为准。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6667` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression vs Stage 02

| Window | Maps regressed | Blockers | Dominant issue |
| --- | --- | ---: | --- |
| `60s` | `soda-creek` | `2` | opening win rate and survival regression |
| `180s` | None | `0` | no same-seed regression |
| `300s` | None | `0` | no same-seed regression, but still no 300s wins |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `1` | soda opening `1` | seed `63100` opening death at `42.5997s` |
| `180s` | `1` | soda opening `1` | same seed `63100` opening death carries forward |
| `300s` | `9` | soda opening `1` / late `2`, caramel late `3`, cracked late `3` | 300 秒 long-run recovery still unresolved |

## 判断

- Narrow map-specific retention improved `cracked-star-jar` 180 秒 and 300 秒 survival, but it reintroduced a `soda-creek` opening regression.
- Continuing from the retention checkpoint without explicit opening replay protection is unsafe.
- Next repair should add hard opening replay retention for `soda-creek` seed `63100` or return to stage 02 baseline before trying another map-specific long-run continuation.

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_soda_cracked_retention_probe.zip`
- `ppo_soda_cracked_retention_probe_metadata.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_stage02.json`
- `window_regression_vs_stage02.md`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
