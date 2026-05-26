# RL Behavior Clone GRU Context8 Entropy002 Training

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_entropy002_smoke.pt`
- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Sample weighting: `danger`
- Entropy regularization: `0.02`
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
- Train accuracy: `0.9158`
- Validation accuracy: `0.8784`
- Validation entropy nats: `0.437509`

## Sequence Diagnostics

- Fully seeded ratio: `0.9856`
- Late low-health ratio: `0.2343`
- Diagnosis flags: none

## Limitations

- This is supervised behavior cloning only and does not prove policy usefulness.
- Entropy regularization is a confidence and action-distribution diagnostic knob; the checkpoint still needs high-pressure 60/300 second comparison and RL policy acceptance review.
