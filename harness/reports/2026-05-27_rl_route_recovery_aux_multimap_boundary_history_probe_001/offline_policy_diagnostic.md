# Behavior Clone Offline Policy Diagnostic

- Gate decision: `offline_policy_diagnostic_recorded_watch_only`
- Model: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_ablation_001/no_class_weight_2_0/staged.pt`
- Samples: `23402`
- Accuracy: `0.5888`
- Dominant predicted action: `3` ratio `0.1732`
- Normalized predicted action entropy: `0.9336`
- Normalized mean policy entropy: `0.6318`

## Phase Summary

| Phase | Samples | Accuracy | Dominant Action | Dominant Ratio | Predicted Entropy |
|---|---:|---:|---:|---:|---:|
| `late` | 6427 | 0.6 | `6` | 0.1478 | 0.94 |
| `mid` | 9917 | 0.6493 | `7` | 0.1909 | 0.9334 |
| `opening` | 7058 | 0.4935 | `3` | 0.2943 | 0.8543 |

## Findings

- No repair finding from offline action-distribution diagnostics.

## Limitations

- Offline behavior clone diagnostics compare model predictions against a dataset only.
- They are not high-pressure Gym comparisons, Replay regression, balance evidence, or RL acceptance.
