# Stage 01 Seed 63402 Guard + Retention Probe

- Decision: `repair_failed`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Anchor model: `harness/reports/2026-05-30_rl_stage01_seed63402_guard_retention_anchor_001/seed63402_guard_retention_anchor.pt`
- Checkpoint: `stage01_seed63402_guard_retention_probe.zip`
- Reward profile: `opening-boundary-escape`

## Results

| Check | Result |
|---|---|
| Training scope | `soda-creek`, seeds `63400-63402`, `256` timesteps |
| Anchor data | `49` opening samples: `17` target guard rows + `32` success retention rows |
| Anchor config | weight `0.5`, interval `256`, `10` KL epochs, anchor lr `0.0005`, `opening_lt_60` only |
| Anchor validation guard | `anchor_validation_guard_failed`; validation KL `2.155758`, argmax agreement `0.6` |
| Training gate | `trained_anchor_validation_guard_failed_not_policy_gate` |
| 60s soda-creek smoke | policy win rate `0.6667`, average survival `52.5218s` |
| Target seed preflight | `policy_target_seed_preflight_failed`; seed `63402` died at `37.4998s`, action `7` ratio `0.0` |
| Failure case | `fail_20260530_008` |

## Conclusion

The combined guard + retention anchor improved the offline training input, but the PPO continuation still failed both the offline anchor guard and the online target seed preflight. The checkpoint shifts seed `63402` into an action `5` dominated defeat path before the intended action `7` escape behavior appears.

This checkpoint must not enter stage 02, stage 03, RL test Bot candidacy, or acceptance. Because the target preflight failed, no full 60 / 180 / 300 second high-pressure matrix was run.

## Validation

- `ppo_training_report.json`: `trained_anchor_validation_guard_failed_not_policy_gate`.
- `comparison_60s.json`: `comparison_recorded_not_balance_gate`.
- `target_seed_preflight.json`: `policy_target_seed_preflight_failed`.
- `failure_case_validation.json`: `failure_cases_valid`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
