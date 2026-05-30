# Stage 01 Seed 63402 Success Retention Samples

- Decision: `retention_anchor_samples_recorded`
- Tool: `tools/export_policy_trace_samples.py`
- Source traces: `harness/reports/2026-05-30_rl_stage01_seed63402_trace_diagnostic_001/parent_traces/`
- Output: `soda_success_opening_retention_samples.jsonl`

## Results

| Check | Result |
|---|---|
| Exported samples | `32` |
| Source seeds | `soda-creek` seeds `63400` and `63401` |
| Time window | `31.9s-37.3s`, matching the seed `63402` guard window |
| Terminal filter | `victory` |
| Action filter | `7,3`; exported rows are all action `7` |
| Boundary filter | `boundary_edge_risk >= 0.75` |
| Observation shape | `observation_len = 145`, `action_count = 9` |
| Behavior clone dry-run | `dataset_validated_not_training_gate` |

## Conclusion

The seed `63402` guard rows only showed the desired local escape action. This report adds the matching successful-opening retention side: two same-map successful parent seeds in the same high-risk opening window, both preserving action `7` as the stable escape behavior.

These rows are training input only. A future stage 01 repair can mix them with target guard rows or use them as a behavior-clone / anchor retention set, but any resulting policy must still pass target-seed preflight, 60 / 180 / 300 second high-pressure comparison, parent no-regression, and failure-case review.

## Validation

- `python3 -m unittest tools/test_export_policy_trace_samples.py`: passed.
- `behavior_clone_dry_run.json`: `dataset_validated_not_training_gate`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
