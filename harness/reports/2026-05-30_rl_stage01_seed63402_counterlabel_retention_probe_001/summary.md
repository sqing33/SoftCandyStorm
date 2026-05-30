# Stage 01 Seed 63402 Counterlabel + Retention Probe

- Decision: `repair_failed`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Anchor model: `harness/reports/2026-05-30_rl_stage01_seed63402_counterlabel_retention_anchor_001/seed63402_counterlabel_retention_anchor.pt`
- Checkpoint: `stage01_seed63402_counterlabel_retention_probe.zip`
- Reward profile: `opening-boundary-escape`

## Results

| Check | Result |
|---|---|
| Training scope | `soda-creek`, seeds `63400-63402`, `256` timesteps |
| Anchor data | `80` opening samples: `48` counterlabel rows + `32` success retention rows |
| Anchor target agreement | `0.75` with dataset actions |
| Anchor config | weight `0.5`, interval `256`, `10` KL epochs, anchor lr `0.0005`, `opening_lt_60` only |
| Anchor validation guard | `anchor_validation_guard_failed`; validation KL `1.971987`, argmax agreement `0.625` |
| Training gate | `trained_anchor_validation_guard_failed_not_policy_gate` |
| 60s soda-creek smoke | policy win rate `0.6667`, average survival `52.5773s` |
| Target seed preflight | `policy_target_seed_preflight_failed`; seed `63402` died at `37.6664s`, action `7` ratio `0.0` |
| Failure case | `fail_20260530_009` |

## Conclusion

The counterlabel + retention anchor improved the offline label shape by eliminating action `5`, but it did not repair the online closed-loop path. Seed `63402` still falls into an action `5` dominated defeat path before the intended action `7` escape behavior appears.

This checkpoint must not enter stage 02, stage 03, RL test Bot candidacy, or acceptance. Because both the anchor guard and target preflight failed, no full 60 / 180 / 300 second high-pressure matrix was run.

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
