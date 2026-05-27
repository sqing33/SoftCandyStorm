# RL Late Risk + Clean Teacher Mix Staged GRU Context8

- Gate decision: `repair_300s_late_window_gap_persists`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_late_risk_clean_teacher_mix_staged_gru_context8_001/staged.pt`
- Opening wrapper: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Failure case: `harness/failed_cases/fail_20260527_034_late_risk_clean_teacher_mix_gap.json`

## Training

This run mixes real clean long-run survival trajectories with the prior edge and late risk repair supervision. It is not clean-teacher-only: the late submodel receives phase-aligned rule Bot trajectory samples, clean `180-300s` survival samples, 60-180 second edge recovery supervision, and 180-300 second risk recovery supervision.

| Source | Samples |
|---|---:|
| Rule / clean teacher trajectory | 13270 |
| Edge recovery supervision | 1040 |
| Risk recovery supervision | 1079 |
| Total late samples | 15389 |

The late submodel uses GRU context8, `map-conditioning = one_hot`, inverse-frequency class weighting, `danger_action_change` sample weighting, `edge_recovery_sample_weight = 4.0`, `risk_recovery_sample_weight = 4.0`, and `entropy_regularization = 0.02`.

| Model | Validation Accuracy | Validation Entropy |
|---|---:|---:|
| `late.pt` | 0.8025 | 0.711786 |

The staged package reuses the previous late-risk `opening.pt` and `mid.pt`, replaces only `late.pt`, and is packaged with `--phase-duration-seconds 300`. Comparisons also use the stage01 PPO opening wrapper for the first 60 seconds.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 100% | 100% | 90% | watch |
| 180s handoff | 3 | 100% | 100% | 100% | comparison evidence only |
| 300s long window | 3 | 0% | 0% | 0% | repair |

The 60s and 180s probes are deterministic and use no stochastic action seed or policy adapter. The mixed model preserves the 180 second handoff gate, but it still cannot survive the 300 second high-pressure long window.

## 300s Failure

All 9 failures occur in `late_180_to_300`, so this run narrows the current failure surface to late-window recovery.

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 231.6205 | `3` / 27.27% | 0.8458 |
| `caramel-workshop` | 3 | 220.3737 | `1` / 22.87% | 0.9073 |
| `cracked-star-jar` | 3 | 227.2076 | `3` / 24.42% | 0.8850 |

Failure analysis is recorded in `failure_analysis_300s.md` and `failure_analysis_300s.json`. Failed-only traces are recorded under `traces/`.

## Interpretation

Adding clean teacher trajectories to late risk supervision improves the dataset quality and preserves the 180 second deterministic handoff probe, but it still does not produce a 300 second survivor on any high-pressure map. This suggests the blocker is no longer basic opening retention or handoff recovery; it needs a closed-loop late survival objective, route planning constraint, upgrade-choice interaction, or a non-imitation policy improvement step that can optimize through 180-300 second pressure.

This report does not permit stage 03, RL policy acceptance, or `rl_test_bot_candidate` promotion.
