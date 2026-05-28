# Stage 02 Soda / Cracked Retention Probe

## 结论

- Gate decision: `soda_cracked_retention_probe_rejected_opening_regression`
- Model: `ppo_soda_cracked_retention_probe.zip`
- Warm start: `harness/reports/2026-05-28_rl_curriculum_stage02_long_run_retention_probe_001/ppo_long_run_retention_probe.zip`
- Failure case: `harness/failed_cases/fail_20260528_070_stage02_soda_cracked_retention_probe_regression.json`
- No-regression report: `window_regression_vs_stage02.md`

本实验从上一轮 `long-run-retention` checkpoint 继续训练，只聚焦 `soda-creek` 和 `cracked-star-jar`，使用 `long-run-retention` reward profile、`4096` timesteps、训练 seed `62800-62802,63100-63102`、learning rate `0.00001`、entropy coefficient `0.03`。目标是验证 map/window-specific retention 是否能修复上一轮 soda/cracked 的 mid/late regression。

结果：probe 被拒绝。它修住了 `cracked-star-jar` 180 秒窗口，并保持 `caramel-workshop` 60/180/300 秒不低于 stage 02 baseline 的同项指标；但 `soda-creek` 60 秒重新出现 opening death，300 秒三图仍全 `0.0`，相对 stage 02 baseline 仍有 `6` 个 no-regression blockers。

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
| `180s` | `soda-creek` | `1` | mid-window survival regression |
| `300s` | `soda-creek`, `cracked-star-jar` | `3` | long-window survival / cracked win regression |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `1` | soda opening `1` | seed `63100` opening death at `42.5997s` |
| `180s` | `1` | soda opening `1` | same seed `63100` opening death carries forward |
| `300s` | `9` | soda opening `1` / late `2`, caramel late `3`, cracked late `3` | 300 秒 long-run recovery still unresolved |

## 判断

- Narrow map-specific retention improved `cracked-star-jar` 180 秒, but it reintroduced a `soda-creek` opening regression.
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
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_180s.json`
- `failure_analysis_180s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
