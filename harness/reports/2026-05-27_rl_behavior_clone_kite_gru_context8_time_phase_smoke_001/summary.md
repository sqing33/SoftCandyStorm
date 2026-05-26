# RL Behavior Clone GRU Context8 Time-Phase Training

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_time_phase_smoke.pt`
- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Time-phase conditioning: `one_hot`
- Sample weighting: `danger`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`

## Dataset

- Movement samples: `21950`
- Episodes: `45`
- Base observation length: `145`
- Sequence input length: `151`
- Total flattened input length: `1208`
- Maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Training

- Epochs: `20`
- Batch size: `256`
- Hidden size: `128`
- Train accuracy: `0.9155`
- Validation accuracy: `0.8754`
- Validation entropy nats: `0.418324`

## Time Phases

| Phase | Count | Ratio |
|---|---:|---:|
| `opening` | 1080 | 0.0492 |
| `mid` | 9332 | 0.4251 |
| `late` | 11538 | 0.5256 |

## Limitations

- This is supervised behavior cloning only and does not prove policy usefulness.
- Time-phase conditioning only exposes run-progress buckets; it does not add upgrade-choice decisions or phase-specific objectives.
