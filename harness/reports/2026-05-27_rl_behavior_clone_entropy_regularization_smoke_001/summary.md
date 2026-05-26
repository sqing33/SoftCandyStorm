# Behavior Clone Entropy Regularization Smoke

- Source: `python/train/train_behavior_clone.py`
- Decision: `behavior_clone_smoke_only_not_policy_gate`
- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Sample limit: `512`
- Entropy regularization: `0.02`

## Result

| Metric | Value |
|---|---:|
| Train samples | 410 |
| Validation samples | 102 |
| Train objective loss | 2.180669 |
| Train cross entropy loss | 2.224144 |
| Train entropy | 2.173753 |
| Train accuracy | 11.22% |
| Validation loss | 2.146053 |
| Validation entropy | 2.174152 |
| Validation accuracy | 13.73% |

## Conclusion

The entropy regularization path trains, records both regularized and plain cross-entropy losses, saves a local smoke checkpoint, and keeps the decision as smoke-only. This is not RL policy acceptance evidence; it only verifies the action-distribution constraint knob before a larger high-pressure comparison experiment.
