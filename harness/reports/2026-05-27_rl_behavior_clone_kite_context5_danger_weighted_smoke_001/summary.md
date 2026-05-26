# RL Behavior Clone Context5 Training

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_danger_weighted_smoke.pt`
- Dataset samples: 19909
- Episodes: 40
- Context frames: 5
- Input observation length: 725
- Sample weighting: `danger`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`

## Final Metrics

| Metric | Value |
|---|---:|
| Train loss | 0.303404 |
| Train accuracy | 0.9156 |
| Validation loss | 0.437333 |
| Validation accuracy | 0.8674 |

## Limitations

- This is an offline movement-clone training smoke, not a policy acceptance gate.
- The model must pass Gym high-pressure 60/300 second rule Bot comparisons before it can be considered as an RL test Bot candidate.
