# Stage 01 Seed 63402 Guard Anchor Probe

- Decision: `repair_failed`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Guard samples: `harness/reports/2026-05-30_rl_stage01_seed63402_target_guard_samples_001/seed63402_target_guard_samples.jsonl`
- Reward profile: `opening-boundary-escape`

## Results

| Check | Result |
|---|---|
| Guard anchor behavior clone | `17` samples, action `7` target distribution, train / validation accuracy `1.0` |
| PPO anchor validation guard | failed: validation KL `4.251955`, argmax agreement `0.0` |
| 60s high-pressure average | `0.7778` |
| 60s `soda-creek` | `0.6667`; seed `63402` still defeated at `37.3331s` |
| 180s high-pressure average | `0.6667` |
| 300s high-pressure average | `0.0` |
| Parent no-regression | `policy_window_regression_passed`, `0` blockers |

## Conclusion

The guard rows are valid and readable, but the first anchor-regularized PPO update did not convert the target state into an online escape trigger. The candidate preserves parent fixed-window metrics but does not improve the target `soda-creek` 60 second blocker, so it must not enter stage 02.

Next repair should strengthen or restructure the local guard objective before another full probe, and must continue to require seed `63402` improvement plus 60 / 180 / 300 second parent no-regression.

## Validation

- `failure_case_validation.json`: `failure_cases_valid`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`; `blocker_audit.json` still reports known project blockers.
