# RL Clean Teacher Late Survival Staged GRU Context8

- Gate decision: `repair_short_window_regression_and_300s_late_gap`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_late_survival_clean_teacher_staged_gru_context8_001/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_032_clean_teacher_late_survival_regression.json`

## Dataset

This run uses only real rule Bot late-window survival trajectories as the late teacher dataset. It does not include edge recovery repair samples, risk recovery repair samples, stochastic evidence, or adapter-derived samples.

| Source | Samples | Episodes | Notes |
|---|---:|---:|---|
| `kite_soda_creek_late_180_300.jsonl` | 3128 | 5 | 4 victories |
| `kite_cracked_star_jar_late_180_300.jsonl` | 2276 | 5 | 2 victories |
| `tank_caramel_workshop_seed62301_late_180_300.jsonl` | 720 | 1 | 1 victory |
| Total clean teacher | 6124 | 11 | 100% trajectory samples |

The clean-teacher dry-run reports 100% late-phase samples, no adapter-derived repair rows, and two watch flags: `high_action_persistence` and `map_sample_imbalance`. Map distribution is `soda-creek` 51.08%, `cracked-star-jar` 37.17%, and `caramel-workshop` 11.76%.

## Training

The late submodel uses GRU context8, `map-conditioning = one_hot`, `time-phase-conditioning = one_hot`, `time-phase-filter = late`, inverse-frequency class weighting, `danger_action_change` sample weighting, and `entropy_regularization = 0.02`.

| Model | Validation Accuracy | Validation Entropy |
|---|---:|---:|
| `late.pt` | 0.7200 | 0.909970 |

The staged package reuses the previous `opening.pt` and `mid.pt`, replaces only `late.pt`, and remains `staged_behavior_clone_packaged_not_policy_gate`.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 80% | 100% | 70% | repair |
| 180s handoff | 3 | 66.67% | 100% | 33.33% | watch |
| 300s long window | 3 | 0% | 0% | 0% | repair |

The 60s and 180s probes are deterministic and use no stochastic action seed or policy adapter. Unlike the previous late-risk auxiliary candidate, this clean-teacher-only late submodel regresses the short-window probes, so it is not usable as a staged policy candidate.

## 300s Failure

The 300s probe fails on all three high-pressure maps. Failed-only traces are recorded under `traces/`, and failure analysis is recorded in `failure_analysis_300s.md` and `failure_analysis_300s.json`.

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 160.5121 | `3` / 30.85% | 0.8011 |
| `caramel-workshop` | 3 | 215.1503 | `3` / 31.76% | 0.8029 |
| `cracked-star-jar` | 3 | 129.9734 | `8` / 25.11% | 0.8267 |

The failure buckets are worse than a pure late-window gap: `soda-creek` and `cracked-star-jar` each include one `opening_lt_60` death, and `cracked-star-jar` also includes one `mid_60_to_180` death.

## Interpretation

The clean teacher direction is useful evidence but not a fix. Using only successful 180-300 second teacher trajectories leaves the late submodel under-regularized for earlier handoff behavior, and the staged policy can enter the late subpolicy during shorter probes because phase thresholds are based on normalized run progress. The caramel teacher slice is also only one episode, so the map-conditioned late policy remains imbalanced.

This report does not permit stage 03, RL policy acceptance, or `rl_test_bot_candidate` promotion. The next repair should either make staged dispatch horizon-safe for short probes, add explicit opening/mid retention to the late replacement experiment, balance the caramel-workshop clean teacher coverage, or switch to closed-loop late survival training with route and low-health recovery objectives.
