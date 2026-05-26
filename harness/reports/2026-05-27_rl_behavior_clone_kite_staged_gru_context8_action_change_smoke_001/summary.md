# RL Behavior Clone Action-Change Staged GRU Context8 Training

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Policy kind: `behavior_clone_staged`
- Phase thresholds: `0.2`, `0.6`
- Subpolicy architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Sample weighting: `danger_action_change`
- Action change weight: `2.0`
- Gate decision: `staged_behavior_clone_packaged_not_policy_gate`

## Phase Training

| Phase | Samples | Train accuracy | Validation accuracy | Validation entropy | Action-change ratio |
|---|---:|---:|---:|---:|---:|
| `opening` | 5388 | 0.8186 | 0.8265 | 0.831901 | 0.2070 |
| `mid` | 9911 | 0.8296 | 0.8153 | 0.717379 | 0.2743 |
| `late` | 6427 | 0.7865 | 0.7704 | 0.807410 | 0.3283 |

## Packaging

- `staged.pt` references `opening.pt`, `mid.pt`, and `late.pt` with relative paths.
- Packaging validation confirmed `action_count = 9` and `base_observation_len = 145` across subpolicies.

## Limitations

- Action-change weighting is a training repair attempt, not a policy gate.
- The staged policy still needs high-pressure comparison and RL policy acceptance review before it can become an RL test Bot candidate.
