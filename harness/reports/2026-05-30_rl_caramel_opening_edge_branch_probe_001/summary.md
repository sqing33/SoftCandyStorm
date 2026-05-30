# Caramel Opening Edge Branch Probe

- Decision: `caramel_opening_narrow_branch_recorded_not_policy_gate`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Target: `caramel-workshop`, seed `63402`, opening action `5` corner lock
- Reward profile: `opening-boundary-escape`

## Result

The broad `0-60s` caramel branch preflight fixed the target opening failure, but it was too loose for long-window use. It changed `171 / 5403` caramel opening decisions, passed the `caramel-workshop:63402` target seed preflight, and raised 60 second caramel win rate from `0.6667` to `1.0`; however, strict parent no-regression failed at `300s/caramel-workshop` because action `5` ratio increased by `0.2746`, above the allowed `0.25` threshold.

The narrower `30-45s` branch kept the useful intervention and removed the broad action drift. It changed exactly one decision across each high-pressure window: seed `63402` at `31.2665s`, original action `5`, target action `7`. The target seed preflight passed with `60.03276s` survival, action `7` ratio `0.38201`, and action `5` ratio `0.208218`.

| Window | Parent caramel win | Narrow branch caramel win | Parent survival | Narrow survival | Regression |
|---|---:|---:|---:|---:|---|
| `60s` | `0.6667` | `1.0` | `53.8329s` | `60.0328s` | passed |
| `180s` | `0.3333` | `0.6667` | `112.6137s` | `158.8058s` | passed |
| `300s` | `0.0` | `0.0` | `120.1944s` | `180.0673s` | passed |

## Validation

- `narrow_target_seed_preflight.json`: `policy_target_seed_preflight_passed`.
- `narrow_window_regression_vs_parent.json`: `policy_window_regression_passed`, `0` blockers.
- `narrow_branch_samples_60s_caramel-workshop_validation.json`: `edge_recovery_samples_valid`.
- `narrow_branch_samples_180s_caramel-workshop_validation.json`: `edge_recovery_samples_valid`.
- `narrow_branch_samples_300s_caramel-workshop_validation.json`: `edge_recovery_samples_valid`.
- Broad `0-60s` comparison is retained as rejected diagnostic evidence in `window_regression_vs_parent.json`.
- Failure case: `harness/failed_cases/fail_20260530_017_caramel_opening_branch_scope.json`.

## Conclusion

The repair target should not be a full `0-60s` caramel opening branch. A much narrower `30-45s` dispatch is enough to move seed `63402` out of the opening death path while preserving 60 / 180 / 300 second parent no-regression on the high-pressure maps.

This is still an evaluation-only diagnostic adapter. It does not approve a learned policy, stage 03, RL test Bot, or acceptance candidate. The remaining caramel problem is late conversion: seeds that reach long windows still do not win at `300s`, so the next repair must combine this narrow opening constraint with a separate `180-300s` hazard / low-health conversion objective.
