# Stage 01 Seed 63402 Edge Recovery Anchor

- Decision: `anchor_trained_not_policy_gate`
- Model: `seed63402_edge_recovery_anchor.pt`
- Edge recovery rows: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_filter_preflight_001/edge_recovery_samples.jsonl`
- Success retention rows: `harness/reports/2026-05-30_rl_stage01_seed63402_success_retention_samples_001/soda_success_opening_retention_samples.jsonl`

## Results

| Check | Result |
|---|---|
| Total samples | `108` |
| Edge recovery rows | `76` filter-derived repair rows |
| Retention rows | `32` successful parent trace rows |
| Map / window | `soda-creek`, `6.8333s-58.9661s` plus retention `31.9s-37.3s` |
| Target action distribution | action `1` = `38/108`, action `7` = `37/108`, action `0` = `23/108`, action `3` = `6/108`, action `5` = `3/108`, action `4` = `1/108` |
| Observation shape | `observation_len = 145`, `action_count = 9` |
| Behavior clone final train accuracy | `0.9767` |
| Behavior clone final validation accuracy | `0.9545` |
| Offline diagnostic | `watch_only`, accuracy `0.9722`, predicted distribution closely matches target |
| Gate decision | `behavior_clone_smoke_only_not_policy_gate` |

## Conclusion

This anchor is the first learned artifact in the seed `63402` chain that captures the edge-recovery filter signal without directly using the hand-written adapter at inference time. It combines filter-derived edge recovery targets with successful retention rows so the target is not only a narrow wall-escape slice.

It is still offline evidence only. The next step is a small PPO anchor-regularized probe that must first pass anchor validation guard and `soda-creek:63402` target preflight before any full fixed-window matrix.

## Validation

- `behavior_clone_anchor_report.json`: `status = trained`, `behavior_clone_smoke_only_not_policy_gate`.
- `offline_policy_diagnostic.json`: `offline_policy_diagnostic_recorded_watch_only`, overall accuracy `0.9722`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete`, no errors.
- `progress_validation.json`: `progress_reports_valid`, no errors; duplicate id warnings are ledger-history warnings.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete`, no errors.
- `goal_consistency.json`: `goal_evidence_consistent`, no errors; current build is still not release-ready.
- `blocker_audit.json`: `goal_blockers_present`, expected blockers remain for manual evidence, release readiness, docs coverage, and roadmap completion.
- `git diff --check`: passed.
