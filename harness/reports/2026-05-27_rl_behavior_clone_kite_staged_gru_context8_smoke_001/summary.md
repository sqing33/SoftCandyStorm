# RL Behavior Clone Staged GRU Context8 Training

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_smoke_001/staged.pt`
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
| `opening` | 1080 | 0.7604 | 0.7361 | 0.996919 |
| `mid` | 9332 | 0.8788 | 0.8569 | 0.583301 |
| `late` | 11538 | 0.8983 | 0.8462 | 0.521772 |

## Packaging

- `staged.pt` references `opening.pt`, `mid.pt`, and `late.pt` with relative paths.
- Packaging validation confirmed `action_count = 9` and `base_observation_len = 145` across subpolicies.

## Limitations

- This report proves staged training and packaging only.
- The staged policy still needs high-pressure comparison and RL policy acceptance review before it can become an RL test Bot candidate.
