# RL Behavior Clone GRU Context8 Map-Conditioned Training

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_map_conditioned_smoke.pt`
- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Sample weighting: `danger`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`

## Dataset

- Movement samples: `21950`
- Episodes: `45`
- Base observation length: `145`
- Sequence input length: `148`
- Total flattened input length: `1184`
- Maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Training

- Epochs: `20`
- Batch size: `256`
- Hidden size: `128`
- Train accuracy: `0.9151`
- Validation accuracy: `0.8790`

## Limitations

- This is supervised behavior cloning only and does not prove policy usefulness.
- The checkpoint must pass high-pressure Gym comparison and RL policy acceptance before it can become an RL test Bot candidate.
