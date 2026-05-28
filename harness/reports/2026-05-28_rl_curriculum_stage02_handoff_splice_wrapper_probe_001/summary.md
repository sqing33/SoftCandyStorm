# Stage 02 Handoff Splice Wrapper Probe

## 结论

- Gate decision: `policy_window_regression_failed`
- Opening model: `../2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Staged fallback: `handoff_splice_fallback.pt`
- Fallback phases: current-failure best for opening/late, current-failure trace incremental fallback for mid
- Phase duration: `300s`
- Evaluation only: no new trained checkpoint
- Failure case: `fail_20260528_086`

本报告验证一个显式 handoff splice：前 `60s` 继续由 stage 02 SB3 opening wrapper 接管，`60-180s` 切到 current-failure trace incremental fallback，`180s` 后切回 current-failure best fallback。目标是看 mid specialist 能否修 180 秒窗口，同时保留 previous best 的 300 秒 late retention。

结果仍失败，不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。该 splice 保住 60 秒窗口，并把 `cracked-star-jar` 180 秒从 current-failure best 的 `0.6667` 提到 `1.0`；但 180 秒 `soda-creek` 平均存活相对 current best 下降 `6.2791s`。300 秒三图仍为 `0.0/0.0/0.0`，并丢掉 current-failure best 的 `cracked-star-jar` `0.3333` 胜率。

## Fixed Windows

| Window | Soda Creek | Caramel Workshop | Cracked Star Jar | Decision |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

Compared with current-failure fallback best, this splice has `4` no-regression blockers: `soda-creek` 180 秒 survival regression, `caramel-workshop` 300 秒 survival regression, `cracked-star-jar` 300 秒 win-rate regression, and `soda-creek` 300 秒 survival regression.

Compared with seed63100 stage 02 baseline, it has `1` strict blocker: `caramel-workshop` 300 秒 average survival drops by `0.0778s`, even though `soda-creek` and `cracked-star-jar` 300 秒 survival improve over the older baseline.

## Failure Analysis

`failure_analysis_300s.md` records `9` failures:

- `soda-creek`: `3` failures, with `1` mid-window failure and `2` late-window failures.
- `caramel-workshop`: `3` failures, with `1` opening failure and `2` late-window failures.
- `cracked-star-jar`: `3` failures, all in `late_180_to_300`.

The splice confirms that a mid specialist can improve one fixed window without preserving late-window wins. The next repair should not package this splice as a candidate. It should either train a constrained fallback that keeps current-failure best as a hard retention anchor, or target the late deaths from this probe with a separate late win-conversion objective.

## Artifacts

- `staged_fallback_report.json`
- `handoff_splice_fallback.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.md`
