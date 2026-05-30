# Stage 01 Seed 63402 Edge Recovery Probe

- Decision: `anchor_validation_guard_failed_not_policy_gate`
- Model: `stage01_seed63402_edge_recovery_probe.zip`
- Parent: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Anchor: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_anchor_001/seed63402_edge_recovery_anchor.pt`
- Datasets: `76` edge recovery rows + `32` success retention rows.

## Results

| Check | Result |
|---|---|
| PPO timesteps | `256` |
| Reward profile | `opening-boundary-escape` |
| Anchor samples | `108`, all `opening_lt_60` |
| Anchor guard | `failed` |
| Validation mean KL | `1.614822` > max `0.25` |
| Validation argmax agreement | `0.2273` < min `0.85` |
| Status | `aborted_by_anchor_validation_guard` |
| Gate decision | `trained_anchor_validation_guard_failed_not_policy_gate` |

## Conclusion

The learned edge recovery anchor is coherent offline, but the closed-loop PPO continuation from the e30 mid-anchor parent does not align with that anchor after the first regularization epoch. The guard correctly stopped the run before target-seed preflight or a full 60/180/300 second fixed-window matrix.

Do not continue this exact configuration. The next repair step should first check start-policy versus edge-recovery-anchor alignment, then either supervised-initialize / distill a compatible SB3 checkpoint or use a narrower constrained branch before any target preflight.

## Validation

- `ppo_training_report.json`: `aborted_by_anchor_validation_guard`.
- `stage01_seed63402_edge_recovery_probe_metadata.json`: records anchor dataset, guard thresholds, and failure metrics.
- `ppo_evaluation_report.json`: smoke evaluation recorded for the aborted checkpoint, but it is not a policy gate.
- Failure case: `harness/failed_cases/fail_20260530_011_stage01_seed63402_edge_recovery_probe_anchor_guard.json`.
- Validators: `validate_failure_cases.py` passed; docs coverage and roadmap remain incomplete with no errors; progress references are valid; goal consistency is coherent not-ready; blocker audit reports expected blockers; `git diff --check` passed.
