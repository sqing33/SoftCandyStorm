# RL Clean Teacher No-Phase Late Survival Staged GRU Context8

- Gate decision: `repair_short_window_regression_and_300s_late_gap`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_late_survival_clean_teacher_no_phase_staged_gru_context8_001/staged.pt`
- Related failure case: `harness/failed_cases/fail_20260527_032_clean_teacher_late_survival_regression.json`

## Purpose

This is a minimal ablation of the clean-teacher-only late survival experiment. It keeps the same 6124 real rule Bot 180-300 second teacher samples and the same staged packaging, but removes `time-phase-conditioning = one_hot` from the late submodel.

The goal is to test whether the short-window regression came mainly from appending explicit phase one-hot features to a late-only subpolicy.

## Training

| Setting | Value |
|---|---|
| Architecture | `gru` |
| Context frames | `8` |
| Map conditioning | `one_hot` |
| Time phase conditioning | `none` |
| Time phase filter | `late` |
| Class weighting | `inverse_frequency` |
| Sample weighting | `danger_action_change` |
| Entropy regularization | `0.02` |

| Model | Validation Accuracy | Validation Entropy |
|---|---:|---:|
| `late.pt` | 0.7331 | 0.922849 |

The dry-run and training diagnostics still report `high_action_persistence` and `map_sample_imbalance`; the dataset remains clean teacher-only and includes no adapter-derived repair samples.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 80% | 100% | 60% | repair |
| 180s handoff | 3 | 66.67% | 100% | 33.33% | watch |
| 300s long window | 3 | 0% | 0% | 0% | repair |

Removing explicit time-phase conditioning did not restore short-window behavior. It slightly improves validation accuracy but leaves deterministic policy quality effectively unchanged.

## 300s Failure

The 300s probe again fails on all three high-pressure maps, with failed-only traces recorded under `traces/` and failure analysis in `failure_analysis_300s.md`.

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 162.8904 | `3` / 31.65% | 0.7933 |
| `caramel-workshop` | 3 | 218.0843 | `3` / 31.34% | 0.8218 |
| `cracked-star-jar` | 3 | 129.9734 | `8` / 25.11% | 0.8267 |

The failure bucket pattern matches the previous clean teacher run: `soda-creek` and `cracked-star-jar` still include `opening_lt_60` deaths, while `caramel-workshop` remains a pure `late_180_to_300` failure.

## Interpretation

This ablation narrows the failure surface. The regression is not caused only by phase one-hot conditioning. The larger issue is that replacing the staged policy's late submodel with a clean teacher-only 180-300 second imitation policy does not preserve shorter-horizon or handoff behavior, and still lacks robust long-run recovery.

This report does not permit stage 03, RL policy acceptance, or `rl_test_bot_candidate` promotion. The next repair should stop treating clean late replacement as a standalone fix and instead add explicit retention/horizon safety, more caramel-workshop teacher coverage, or closed-loop late survival training.
