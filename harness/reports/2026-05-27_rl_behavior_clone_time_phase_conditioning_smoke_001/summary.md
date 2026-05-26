# RL Behavior Clone Time-Phase Conditioning Smoke

- Status: `trained`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_time_phase_conditioning_smoke_001/model.pt`
- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Time-phase conditioning: `one_hot`
- Limit samples: `512`

## Training

- Train samples: `410`
- Validation samples: `102`
- Epochs: `1`
- Hidden size: `32`
- Train accuracy: `0.1098`
- Validation accuracy: `0.2941`
- Validation entropy nats: `2.163633`

## Time Phases

| Phase | Count | Ratio |
|---|---:|---:|
| `opening` | 0 | 0.0000 |
| `mid` | 179 | 0.3496 |
| `late` | 333 | 0.6504 |

## Limitations

- This is a small CLI smoke only; it does not prove policy quality.
- The checkpoint must pass full training, high-pressure 60/300 second comparison, and RL policy acceptance before it can become an RL test Bot candidate.
