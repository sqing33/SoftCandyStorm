# RL Late-Risk Aux Staged GRU Context8

- Gate decision: `repair_300s_late_window_gap_persists`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_late_risk_aux_staged_gru_context8_001/staged.pt`
- Opening wrapper: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Failure case: `harness/failed_cases/fail_20260527_031_edge_aux_handoff_window_late_gap.json`

## Training

This run keeps the staged opening wrapper, reuses the staged behavior-clone packaging flow, and retrains the late subpolicy with 180-300 second risk recovery supervision.

| Source | Samples |
|---|---:|
| Rule Bot trajectory | 6427 |
| Edge recovery supervision | 1040 |
| Risk recovery supervision | 1079 |
| Total late samples | 8546 |

The late submodel uses GRU context8, `map-conditioning = one_hot`, inverse-frequency class weighting, `danger_action_change` sample weighting, `edge_recovery_sample_weight = 4.0`, `risk_recovery_sample_weight = 4.0`, and `entropy_regularization = 0.02`.

| Model | Validation Accuracy | Validation Entropy |
|---|---:|---:|
| `late.pt` | 0.7238 | 0.816660 |

The packaged staged policy is self-contained and records `opening.pt`, `mid.pt`, and `late.pt` as subpolicies. Packaging remains `staged_behavior_clone_packaged_not_policy_gate`.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 100% | 100% | 100% | comparison evidence only |
| 180s handoff | 3 | 100% | 100% | 100% | comparison evidence only |
| 300s long window | 3 | 0% | 0% | 0% | repair |

The 60s and 180s probes remain deterministic and use no stochastic action seed or policy adapter. They confirm the late-risk auxiliary retrain did not break the short opening or 180 second handoff probes, but they do not permit stage 03 or RL policy acceptance.

## 300s Failure

The 300s probe fails on all three high-pressure maps. All 9 failures occur in the `late_180_to_300` bucket.

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 229.4423 | `3` / 24.39% | 0.8452 |
| `caramel-workshop` | 3 | 221.5628 | `1` / 17.98% | 0.9173 |
| `cracked-star-jar` | 3 | 258.4569 | `8` / 20.53% | 0.8665 |

Failure analysis is recorded in `failure_analysis_300s.md` and `failure_analysis_300s.json`. Failed-only traces are recorded under `traces/`.

## Interpretation

Late risk recovery supervision is now wired through dry-run, training, weighting, staged packaging, deterministic comparison, and failure analysis. The experiment is useful repair evidence, but it does not fix the long-window blocker: the 300 second high-pressure probe regresses `cracked-star-jar` from the prior 33.33% comparison to 0% and leaves `soda-creek` and `caramel-workshop` at 0%.

The next repair should stop relying only on hand-written adapter imitation. Prefer real long-run survival trajectory, explicit 180-300 second route / low-health recovery objectives, hazard + boss joint pressure handling, or closed-loop PPO with late survival rewards and route constraints. This report does not permit stage 03, RL policy acceptance, or `rl_test_bot_candidate` promotion.
