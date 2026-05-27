# Route Recovery Behavior Clone Smoke

- Gate decision: `behavior_clone_smoke_only_not_policy_gate`
- Training report: `harness/reports/2026-05-27_rl_route_recovery_behavior_clone_smoke_001/run_output.json`
- Smoke model: `harness/reports/2026-05-27_rl_route_recovery_behavior_clone_smoke_001/route_recovery_behavior_clone_smoke.pt`
- Source samples: `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/route_recovery_samples.jsonl`

## Dataset

The smoke uses `689` `edge_recovery_supervision_sample` rows exported from route_recovery trace hotspots across `soda-creek`, `caramel-workshop`, and `cracked-star-jar`. Observation length is `145`, minimum health ratio is `0.2867`, and all samples are marked as `repair_training_input`.

## Training

The 1 epoch MLP smoke completed and wrote a checkpoint. Validation accuracy was `0.6522`, validation entropy was `2.193724` nats, and `edge_recovery_sample_weight = 4.0` was applied to all training rows.

## Limitations

- This is a dataset/training-path smoke only.
- The model is not a playable policy candidate.
- It does not replace deterministic 60 / 180 / 300 second high-pressure comparisons.
- It does not permit Stage 03, RL acceptance, or `rl_test_bot_candidate` promotion.
