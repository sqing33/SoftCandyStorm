# RL Clean Teacher Absolute Phase Staged GRU Context8

- Gate decision: `repair_short_window_regression_and_300s_late_gap`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_late_survival_clean_teacher_absolute_phase_staged_gru_context8_001/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_032_clean_teacher_late_survival_regression.json`

## Packaging

This run repackages the clean teacher staged policy with `--phase-duration-seconds 300`. The checkpoint records `phase_dispatch = absolute_time_seconds`, so Gym evaluation dispatches opening / mid / late from `time_seconds / 300` rather than from each probe's normalized observation progress.

The submodels are unchanged from the clean teacher run:

- `opening.pt`: previous staged opening submodel.
- `mid.pt`: previous staged mid submodel.
- `late.pt`: clean teacher-only late survival submodel trained from real 180-300 second rule Bot trajectories.

This packaging tests whether horizon-safe staged dispatch restores short-window probes. It does not train a new policy.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 70% | 100% | 80% | watch |
| 180s handoff | 3 | 66.67% | 100% | 33.33% | watch |
| 300s long window | 3 | 0% | 0% | 0% | repair |

The 60s and 180s probes are deterministic and use no stochastic action seed, opening wrapper, upgrade ranker, or policy adapter. Absolute phase dispatch did not restore the short-window regression: `soda-creek` still has opening deaths, and `cracked-star-jar` still underperforms the strongest rule Bot in the 180s comparison.

## 300s Failure

The 300s probe fails on all three high-pressure maps. Failed-only traces are recorded under `traces/`, and failure analysis is recorded in `failure_analysis_300s.md` and `failure_analysis_300s.json`.

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 160.5121 | `3` / 30.85% | 0.8011 |
| `caramel-workshop` | 3 | 215.1503 | `3` / 31.76% | 0.8029 |
| `cracked-star-jar` | 3 | 129.9734 | `8` / 25.11% | 0.8267 |

Failure buckets:

- `soda-creek`: 1 opening death and 2 late deaths.
- `caramel-workshop`: 3 late deaths.
- `cracked-star-jar`: 1 opening death, 1 mid death, and 1 late death.

## Interpretation

Absolute-time dispatch fixes the evaluation plumbing, but it does not fix the clean teacher-only strategy. The late submodel still lacks opening / mid retention and long-run recovery objectives, and the clean teacher dataset remains imbalanced toward `soda-creek` and `cracked-star-jar` with only one clean `caramel-workshop` teacher episode.

This report does not permit stage 03, RL policy acceptance, or `rl_test_bot_candidate` promotion. The next repair should stop retesting clean teacher-only packaging by itself and instead add retention or contrastive data, expand `caramel-workshop` clean teacher coverage, or move to closed-loop late survival training with route, low-health, hazard, and boss-pressure objectives.
