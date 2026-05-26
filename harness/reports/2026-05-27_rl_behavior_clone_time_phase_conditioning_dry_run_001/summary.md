# RL Behavior Clone Time-Phase Conditioning Dry Run

- Mode: `dry_run`
- Gate decision: `dataset_validated_not_training_gate`
- Architecture target: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Time-phase conditioning: `one_hot`
- Thresholds: `0.2`, `0.6`

## Dataset

- Movement samples: `21950`
- Maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- Fully seeded ratio: `0.9856`
- Late low-health ratio: `0.2343`
- Sequence diagnosis flags: none

## Time Phases

| Phase | Count | Ratio |
|---|---:|---:|
| `opening` | 1080 | 0.0492 |
| `mid` | 9332 | 0.4251 |
| `late` | 11538 | 0.5256 |

## Limitations

- This report only proves the feature path and dataset diagnostics; it does not train or evaluate a policy.
- A time-phase-conditioned checkpoint still needs high-pressure 60/300 second comparison and RL policy acceptance review.
