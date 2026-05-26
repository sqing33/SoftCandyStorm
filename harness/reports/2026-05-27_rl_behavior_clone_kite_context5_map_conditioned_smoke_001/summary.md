# RL Behavior Clone Context5 Map Conditioned Training

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_map_conditioned_smoke.pt`
- Status: `trained`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`
- Context frames: `5`
- Map conditioning: `one_hot`
- Input observation len: `728`
- Base observation len: `145`
- Training samples: `17560`
- Validation samples: `4390`

## Final Metrics

| Epoch | Train loss | Train accuracy | Validation loss | Validation accuracy |
|---:|---:|---:|---:|---:|
| 20 | 0.302158 | 0.9137 | 0.448146 | 0.8551 |

## Dataset Mix

| Map | Samples | Ratio |
|---|---:|---:|
| `caramel-workshop` | 6920 | 0.3153 |
| `cracked-star-jar` | 9641 | 0.4392 |
| `soda-creek` | 5389 | 0.2455 |

## Limitations

- Training accuracy and validation accuracy are not policy acceptance evidence.
- This model still requires Gym high-pressure 60/300 second comparisons and RL acceptance validation before any candidate promotion.

