# RL Edge Recovery Behavior Clone Dataset Smoke

- Decision: `behavior_clone_smoke_only_not_policy_gate`
- Dry run: `harness/reports/2026-05-27_rl_edge_recovery_behavior_clone_dataset_smoke_001/dry_run.json`
- Training smoke: `harness/reports/2026-05-27_rl_edge_recovery_behavior_clone_dataset_smoke_001/run_output.json`
- Smoke model: `harness/reports/2026-05-27_rl_edge_recovery_behavior_clone_dataset_smoke_001/edge_recovery_behavior_clone_smoke.pt`

## Dataset

`train_behavior_clone.py` now accepts `edge_recovery_supervision_sample` records as movement repair targets. The smoke dataset contains `2215` samples from `soda-creek / 62201`; all are marked as `edge_recovery_supervision`, preserve observation length `145`, and force the movement action space to the 9-direction Gym action set.

## Training Smoke

The 1 epoch MLP smoke completed with validation accuracy `0.8036` and validation entropy `2.095966` nats. This only proves the repair samples can enter the supervised movement training path; it is not a usable policy gate, not a deterministic high-pressure result, and not RL acceptance evidence.

## Next

Use these samples as an auxiliary handoff recovery constraint together with existing trajectory data, then rerun 60 second high-pressure opening gate and 180 second staged policy comparison before considering any stage 03 work.
