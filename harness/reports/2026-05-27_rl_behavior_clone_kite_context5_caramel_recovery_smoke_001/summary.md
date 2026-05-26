# RL Behavior Clone Context5 Caramel Recovery Training

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_caramel_recovery_smoke.pt`
- Dataset samples: 21950
- Context frames: 5
- Sample weighting: `danger`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`

## Final Metrics

| Metric | Value |
|---|---:|
| Train loss | 0.295967 |
| Train accuracy | 0.9153 |
| Validation loss | 0.458690 |
| Validation accuracy | 0.8524 |

## Limitations

- This is an offline movement-clone training smoke.
- It must be judged by Gym high-pressure 60/300 second rule Bot comparisons.
