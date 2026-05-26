# RL Behavior Clone Action-Change Weighting Smoke

- Feature: `--sample-weighting action_change|danger_action_change`
- Smoke command: opening phase GRU context8, `limit-samples 512`, `epochs 1`
- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Gate decision: `behavior_clone_smoke_only_not_policy_gate`

## Result

- Status: `trained`
- Samples after opening phase filter: `180`
- Sample weighting mode: `danger_action_change`
- Action change weight: `2.0`
- Action change samples in training sampler: `27`
- Action change sample ratio: `0.1875`
- Weight range: `1.0` to `3.0`

## Limitations

- This smoke only proves the training knob and report shape.
- It does not evaluate policy quality, balance, fun, or RL test Bot readiness.
