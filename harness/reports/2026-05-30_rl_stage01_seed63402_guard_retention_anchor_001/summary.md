# Stage 01 Seed 63402 Guard + Retention Anchor

- Decision: `anchor_trained_not_policy_gate`
- Model: `seed63402_guard_retention_anchor.pt`
- Target guard rows: `harness/reports/2026-05-30_rl_stage01_seed63402_target_guard_samples_001/seed63402_target_guard_samples.jsonl`
- Success retention rows: `harness/reports/2026-05-30_rl_stage01_seed63402_success_retention_samples_001/soda_success_opening_retention_samples.jsonl`

## Results

| Check | Result |
|---|---|
| Total samples | `49` |
| Guard rows | `17` edge recovery supervision rows |
| Retention rows | `32` successful parent trace rows |
| Map / window | `soda-creek`, `31.9999s-37.2664s` |
| Action distribution | action `7` = `49/49` |
| Observation shape | `observation_len = 145`, `action_count = 9` |
| Train accuracy | `1.0` |
| Validation accuracy | `1.0` |
| Gate decision | `behavior_clone_smoke_only_not_policy_gate` |

## Conclusion

The combined anchor now represents both sides of the seed `63402` opening repair target: the failing seed's target guard rows and successful same-map parent trajectories in the same opening window. It is a better local anchor input than the 17-row guard-only anchor, but it is still offline evidence only.

The next repair run may use this model as a behavior-clone anchor or supervised initialization, then must first pass `soda-creek:63402` target-seed preflight before any full 60 / 180 / 300 second high-pressure and parent no-regression matrix is considered meaningful.

## Validation

- `behavior_clone_anchor_report.json`: `status = trained`, `behavior_clone_smoke_only_not_policy_gate`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete`, 20 / 20 docs tracked, 18 docs still partial.
- `progress_validation.json`: `progress_reports_valid`, 589 / 589 report references exist; duplicate recent ids are warnings only because they are recorded in both completed and current findings.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete`, 11 / 11 phases tracked, 8 phases still incomplete.
- `goal_consistency.json`: `goal_evidence_consistent`; docs, roadmap, release candidate evidence, and package manifest consistently report not-ready.
- `blocker_audit.json`: `goal_blockers_present`, with P0 manual evidence gaps plus release, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
