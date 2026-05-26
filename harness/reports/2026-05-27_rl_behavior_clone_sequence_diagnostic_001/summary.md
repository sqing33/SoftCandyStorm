# Behavior Clone Sequence Diagnostic

- Source: `python/train/train_behavior_clone.py --dry-run`
- Decision: `dataset_validated_not_training_gate`
- Architecture target: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Samples: `21950`

## Sequence Signals

| Signal | Value |
|---|---:|
| Fully seeded context ratio | 98.56% |
| Average missing context frames | 0.0238 |
| Average sequence span | 7.5099 s |
| Same-action transition ratio | 64.47% |
| Late low-health sample ratio | 23.43% |

## Map Coverage

| Map | Samples |
|---|---:|
| `caramel-workshop` | 6920 |
| `cracked-star-jar` | 9641 |
| `soda-creek` | 5389 |

## Diagnosis Flags

- None

## Conclusion

The GRU context8 failure is not explained by missing context padding, absent late low-health coverage, or a sequence dry-run shape error. The next repair should focus on action distribution constraints, staged policy targets, PPO distillation initialization, or loss/objective changes before running another large recurrent training pass.
