# Stage 01 Seed 63402 Edge Recovery Branch Preflight

- Decision: `conditional_branch_preflight_passed_not_policy_gate`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Adapter: `edge_recovery_branch`
- Scope: `soda-creek`, seeds `63400-63402`, `60s`

## Results

| Check | Result |
|---|---|
| 60s comparison gate | `comparison_recorded_not_balance_gate` |
| Policy win rate | `1.0` |
| Average survival | `60.0328s` |
| Target seed preflight | `policy_target_seed_preflight_passed` |
| Target seed `63402` | victory at `60.0328s`, action `7` ratio `0.372016` |
| Overall action `7` ratio | `0.4525` |
| Branch usage | `4 / 5403` decisions, ratio `0.0007` |
| Branch samples | `4`, `edge_recovery_samples_valid` |

## Conclusion

The constrained edge recovery branch fixes the `soda-creek:63402` 60 second target preflight without repeating the previous global action `7` collapse. The branch only dispatches when the base policy chooses a wallward action under the configured map/time/boundary/pressure conditions, and the branch action itself is non-wallward.

This is still an evaluation-only diagnostic adapter, not RL acceptance evidence. The useful next step is to check whether the same conditioned branch stays clean under broader parent no-regression windows before considering any learned-policy promotion.

## Validation

- `comparison_60s.json`: `comparison_recorded_not_balance_gate`.
- `target_seed_preflight.json`: `policy_target_seed_preflight_passed`.
- `edge_recovery_branch_samples_validation.json`: `edge_recovery_samples_valid`.
- `progress_validation.json`: `progress_reports_valid`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no errors.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual/release/docs/roadmap blockers.
- `py_compile`: passed for `train_sb3.py`, `test_train_sb3.py`, `validate_edge_recovery_samples.py`, and validator tests.
- `pytest`: `61 passed` for `python/train/test_train_sb3.py` and `tools/test_validate_edge_recovery_samples.py`.
