# Behavior Clone Offline Policy Diagnostic

- Gate decision: `offline_policy_diagnostic_recorded_watch_only`
- Model: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/staged.pt`
- Samples: `22415`
- Accuracy: `0.618`
- Dominant predicted action: `7` ratio `0.1506`
- Normalized predicted action entropy: `0.9434`
- Normalized mean policy entropy: `0.6498`

## Phase Summary

| Phase | Samples | Accuracy | Dominant Action | Dominant Ratio | Predicted Entropy |
|---|---:|---:|---:|---:|---:|
| `late` | 6469 | 0.5981 | `6` | 0.1469 | 0.94 |
| `mid` | 10253 | 0.6542 | `7` | 0.1858 | 0.9376 |
| `opening` | 5693 | 0.5754 | `4` | 0.1902 | 0.9159 |

## Findings

- No repair finding from offline action-distribution diagnostics.

## Limitations

- Offline behavior clone diagnostics compare model predictions against a dataset only.
- They are not high-pressure Gym comparisons, Replay regression, balance evidence, or RL acceptance.
