# Route Recovery Auxiliary Staged Smoke

- Gate decision: `behavior_clone_smoke_only_not_policy_gate`
- Staged model: `harness/reports/2026-05-27_rl_route_recovery_aux_staged_smoke_001/staged.pt`
- Packaging report: `harness/reports/2026-05-27_rl_route_recovery_aux_staged_smoke_001/packaging.json`
- Failure case: `harness/failed_cases/fail_20260527_039_route_recovery_aux_staged_smoke_action_collapse.json`

## Dataset Mix

This smoke combines the phase-aligned KiteBot high-pressure trajectories with the `689` route_recovery repair samples. Opening excludes all route recovery samples, mid keeps `342` samples from `60-180s`, and late keeps `40` samples after phase filtering.

| Phase | Samples | Route Recovery Samples | Validation Accuracy | Validation Entropy |
|---|---:|---:|---:|---:|
| `opening` | 5388 | 0 | 0.4109 | 2.104974 |
| `mid` | 10253 | 342 | 0.3774 | 1.908970 |
| `late` | 6467 | 40 | 0.3078 | 2.076900 |

All three submodels use GRU context8, map one-hot, time-phase one-hot, inverse-frequency class weighting, `danger_action_change`, `edge_recovery_sample_weight = 4.0`, and `entropy_regularization = 0.02`.

## Load Smoke

The staged checkpoint packages with absolute-time dispatch over a 300 second horizon and loads through the Gym evaluation path. A 5 second `soda-creek` smoke completed, but the deterministic policy selected action `7` on `151/151` frames, so the model is explicitly not a policy candidate.

## Limitations

- This is a mixed-dataset and staged-packaging smoke only.
- The 5 second load smoke is not a high-pressure gate.
- The action-collapse failure case must remain attached to this checkpoint.
- The checkpoint cannot enter Stage 03, RL acceptance, or `rl_test_bot_candidate` review.
