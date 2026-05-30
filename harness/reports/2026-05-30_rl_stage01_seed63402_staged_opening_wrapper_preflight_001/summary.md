# Stage 01 Seed 63402 Staged Opening Wrapper Preflight

- Decision: `repair_failed`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Opening seconds: `60`
- Reward profile: `opening-boundary-escape`

## Results

| Check | Result |
|---|---|
| Evaluation scope | `soda-creek`, seeds `63400-63402`, `60s` |
| Policy win rate | `0.6667` |
| Average survival | `52.1773s` |
| Target seed preflight | `policy_target_seed_preflight_failed` |
| Target seed `63402` | defeat at `36.4665s`, action `7` ratio `0.0` |
| Target seed action counts | action `4` = `906`, action `2` = `188`, action `7` = `0` |
| Failure case | `fail_20260530_010` |

## Conclusion

The generic stage01 `corner_risk_delta` opening wrapper does not repair seed `63402`. It removes the previous action `5` dominance but replaces it with an action `4` dominated defeat path, and the target seed still never reaches action `7`.

This wrapper must not be used as the seed `63402` opening repair branch. The next branch needs seed-specific trace supervision or explicit constrained dispatch before any full fixed-window matrix is meaningful.

## Validation

- `comparison_60s.json`: `comparison_recorded_not_balance_gate`.
- `target_seed_preflight.json`: `policy_target_seed_preflight_failed`.
- `failure_case_validation.json`: `failure_cases_valid`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
