# RL Behavior Clone Edge Aux Entropy Class Staged GRU Context8

- Gate decision: `opening_gate_failed_not_run_180s`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/staged.pt`
- Training data: phase-aligned high-pressure KiteBot trajectories plus `2215` edge recovery supervision samples
- Edge recovery sample weight: `4.0`
- Class weighting: `inverse_frequency`
- Entropy regularization: `0.02`
- Failure case: `harness/failed_cases/fail_20260527_029_edge_aux_entropy_class_opening_gap.json`

## Training

| Phase | Samples | Edge samples | Validation accuracy | Validation entropy |
|---|---:|---:|---:|---:|
| `opening` | 5591 | 203 | 0.8184 | 0.838081 |
| `mid` | 10883 | 972 | 0.8016 | 0.798353 |
| `late` | 7467 | 1040 | 0.8084 | 0.700317 |

## 60 Second Gate

The 60 second high-pressure comparison used `10` seeds starting at `62400`. Action distribution improved compared with the previous edge auxiliary clone, but the opening gate still failed:

| Map | Win rate | Action entropy bits | Dominant action |
|---|---:|---:|---|
| `soda-creek` | 0.50 | 1.6725 | `3` at 66.58% |
| `caramel-workshop` | 0.90 | 2.0406 | `3` at 57.53% |
| `cracked-star-jar` | 0.90 | 2.1726 | `3` at 48.13% |

Because `soda-creek` is still below the opening hard gate, the 180 second handoff comparison was not run. This is repair evidence only and cannot proceed to stage 03 or RL policy acceptance.

## Next

The next attempt should stop treating edge recovery samples as a broad mixed clone fix. Prefer either explicit stage 01 opening retention or a handoff-only/mid-window constraint after opening is preserved.
