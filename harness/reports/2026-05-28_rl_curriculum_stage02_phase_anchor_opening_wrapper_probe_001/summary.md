# Stage 02 Phase Anchor Opening Wrapper Probe

## 结论

- Gate decision: `policy_window_regression_failed`
- Wrapper: `stage_02_late_180_to_300.zip` before `60s`, then `ppo_phase_specific_anchor_smoke.zip`
- Opening model: `../2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Fallback model: `../2026-05-28_rl_curriculum_stage02_phase_specific_anchor_smoke_001/ppo_phase_specific_anchor_smoke.zip`
- Evaluation only: no new checkpoint trained
- Failure case: `fail_20260528_085`

本报告验证显式 opening wrapper 是否能把上一轮 phase-specific anchor PPO 的 60 秒 opening blocker 隔离出来。结果仍失败，不能推进 stage 03、`rl_test_bot_candidate` 或 RL acceptance。

Wrapper 让 `soda-creek` 60 秒从 `0.6667` 回到 `1.0`，说明显式 opening freeze 能修补短窗。但 180 秒 `soda-creek` 从 phase-specific anchor PPO 的 `0.6667` 掉到 `0.3333`，300 秒三图仍全为 `0.0`，说明问题转移到 handoff / mid-window fallback 与 late-window survival。

## Fixed Windows

| Window | Soda Creek | Caramel Workshop | Cracked Star Jar | Decision |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

Compared with the phase-specific anchor PPO without wrapper, this wrapper has `3` no-regression blockers: `soda-creek` 180s win-rate regression, plus `cracked-star-jar` and `soda-creek` 300s survival regressions.

Compared with current-failure fallback best, it has `5` blockers. Compared with the seed63100 stage02 baseline, it has `2` blockers.

## Failure Analysis

`failure_analysis_300s.md` records `9` failures:

- `soda-creek`: `3` failures, now with `2` mid-window failures and `1` late-window failure.
- `caramel-workshop`: `3` failures, with `1` opening failure and `2` late-window failures.
- `cracked-star-jar`: `3` failures, with `1` mid-window failure and `2` late-window failures.

The wrapper confirms that short-window opening protection alone is not enough. The next repair should focus on the 60-180s handoff and mid/late constrained fallback behavior, especially `soda-creek` post-wrapper deaths at `70.1326s` and `163.5393s`.

## Artifacts

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_phase_specific_anchor.md`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.md`
