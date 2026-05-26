# RL Behavior Clone Phase-Aligned Staged GRU Context8 Training

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_phase_aligned_smoke_001/staged.pt`
- Policy kind: `behavior_clone_staged`
- Phase thresholds: `0.2`, `0.6`
- Subpolicy architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Sample weighting: `danger`
- Gate decision: `staged_behavior_clone_packaged_not_policy_gate`

## Phase Training

| Phase | Samples | Train accuracy | Validation accuracy | Validation entropy |
|---|---:|---:|---:|---:|
| `opening` | 5388 | 0.8494 | 0.8098 | 0.687015 |
| `mid` | 9911 | 0.8562 | 0.8148 | 0.630046 |
| `late` | 6427 | 0.8077 | 0.7634 | 0.755121 |

## Packaging

- `staged.pt` references `opening.pt`, `mid.pt`, and `late.pt` with relative paths.
- Packaging validation confirmed `action_count = 9` and `base_observation_len = 145` across subpolicies.

## Limitations

- Phase-aligned trajectory export improved the training data semantics but did not prove policy quality.
- The staged policy still needs high-pressure comparison and RL policy acceptance review before it can become an RL test Bot candidate.
