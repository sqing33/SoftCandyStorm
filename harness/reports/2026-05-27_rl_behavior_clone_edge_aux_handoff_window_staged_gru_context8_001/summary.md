# RL Edge-Aux Handoff-Window Staged GRU Context8

- Gate decision: `repair_300s_late_window_gap`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_staged_gru_context8_001/staged.pt`
- Opening wrapper: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Failure case: `harness/failed_cases/fail_20260527_031_edge_aux_handoff_window_late_gap.json`

## Training

This run keeps edge recovery supervision out of the opening submodel and limits repair samples to the 60-180 second handoff window before phase filtering.

| Phase | Samples | Edge Samples | Validation Accuracy | Validation Entropy |
|---|---:|---:|---:|---:|
| `opening` | 5388 | 0 | 0.8163 | 0.828550 |
| `mid` | 10710 | 799 | 0.8231 | 0.687777 |
| `late` | 7467 | 1040 | 0.8084 | 0.700317 |

All three submodels use GRU context8, `map-conditioning = one_hot`, inverse-frequency class weighting, `danger_action_change` sample weighting, `edge_recovery_sample_weight = 4.0`, and `entropy_regularization = 0.02`.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 100% | 100% | 100% | passed as comparison evidence |
| 180s handoff | 3 | 100% | 100% | 100% | passed as comparison evidence |
| 300s long window | 3 | 0% | 0% | 33.33% | repair |

The 60s and 180s results are deterministic and use no stochastic action seed or policy adapter. The original `soda-creek / 62201` and `cracked-star-jar / 62201` handoff failures are no longer reproduced in the 180s probe.

## 300s Failure

The 300s probe fails in the `late_180_to_300` bucket:

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 237.2439 | `3` / 29.07% | 0.7972 |
| `caramel-workshop` | 3 | 220.2403 | `5` / 17.95% | 0.9252 |
| `cracked-star-jar` | 2 | 207.0152 | `3` / 35.00% | 0.8025 |

Failure analysis is recorded in `failure_analysis_300s.md` and `failure_analysis_300s.json`.

## Interpretation

The handoff-window filter is a real improvement over the previous edge-aux staged clone: opening is preserved and the 180 second deterministic handoff gap is closed. The model is still not a policy candidate, because the 300 second probe exposes a new late-window survival gap across all three high-pressure maps.

Next repair should target 180-300 second pressure recovery with late-window traces, stronger late objectives, or additional long-run supervision. This report does not permit stage 03 or RL policy acceptance.
