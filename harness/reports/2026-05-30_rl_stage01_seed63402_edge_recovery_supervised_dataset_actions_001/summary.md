# Stage 01 Seed 63402 Edge Recovery Supervised Dataset Actions

- Decision: `target_preflight_passed_but_action_collapse_not_policy_gate`
- Model: `seed63402_edge_recovery_supervised_dataset_actions.zip`
- Target mode: `dataset_actions`
- Samples: `108` edge recovery + retention rows.

## Results

| Check | Result |
|---|---|
| Distillation validation argmax accuracy | `0.8182` |
| Action distribution guard | `passed` |
| Combined anchor alignment | `passed`, mean KL `0.207452`, argmax agreement `0.9444` |
| Edge rows alignment | `passed`, mean KL `0.235855`, argmax agreement `0.9211` |
| Retention rows alignment | `passed`, mean KL `0.139997`, argmax agreement `1.0` |
| `soda-creek:63402` target preflight | `passed`, `60.0328s` victory, action `7` ratio `0.99889` |
| `soda-creek` 60s comparison | `repair`, win rate `0.6667`, action `7` ratio `0.9987` |
| Regression symptom | seed `63400` died at `30.1666s` |

## Conclusion

Hard-label supervised initialization can make an SB3 checkpoint match the edge recovery anchor offline and pass the target seed preflight, but the resulting online policy collapses into almost always choosing action `7`. This is not a policy gate and must not proceed to 180/300 second windows.

The next repair should keep the edge recovery action only under a state-conditioned constraint, such as an opening branch or policy adapter that dispatches on boundary/enemy-pressure features, instead of training a full opening policy to emit action `7` globally.

## Validation

- `distillation_report.json`: `sb3_distillation_smoke_only_not_policy_gate`, action distribution guard passed.
- `alignment_combined.json`: `behavior_clone_anchor_alignment_within_thresholds`.
- `comparison_60s.json`: `comparison_recorded_needs_action_bias_repair`.
- `target_seed_preflight.json`: `policy_target_seed_preflight_passed` for `soda-creek:63402`.
- Failure case: `harness/failed_cases/fail_20260530_013_stage01_seed63402_supervised_init_action_collapse.json`.
- Validators: `validate_failure_cases.py` passed; docs coverage and roadmap remain incomplete with no errors; progress references are valid; goal consistency is coherent not-ready; blocker audit reports expected blockers; `git diff --check` passed.
