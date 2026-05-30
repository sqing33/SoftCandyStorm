# RL Edge Branch + Late Filter Chain Smoke

- Decision: `adapter_chain_smoke_passed_not_policy_gate`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Edge branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Scope: single `soda-creek` smoke, seed `63402`, `5s`

## Result

The CLI now allows `--edge-recovery-branch-model` and `--late-recovery-filter` to be used together during evaluation. The generated `evaluation.json` reports a `late_recovery_filter` adapter whose `wrapped_policy_kind` is `edge_recovery_branch`, and the nested `wrapped_policy_adapter` preserves the edge branch configuration and usage report.

This smoke deliberately does not claim policy quality. It only verifies that stage 01 opening branch diagnostics can be composed with late-window recovery diagnostics without losing adapter provenance or sample export plumbing.

## Validation

- `python3 -m py_compile python/train/train_sb3.py python/train/test_train_sb3.py`: passed.
- `uv run --with pytest python -m pytest python/train/test_train_sb3.py tools/test_validate_edge_recovery_samples.py`: `59 passed, 4 skipped`.
- `evaluation.json`: adapter chain recorded.
- `edge_branch_late_filter_samples.jsonl`: `0` rows for this short smoke, as expected because neither the opening branch nor the late filter changed an action within `5s`.
- `progress_validation.json`: progress references valid.
- `docs_implementation_coverage_validation.json`: docs coverage ledger structurally valid with active Goal incompleteness allowed.
- `roadmap_phase_audit_validation.json`: roadmap audit structurally valid with active Goal incompleteness allowed.
- `goal_evidence_consistency.json`: Goal evidence references consistent.
- `goal_blockers_audit.json`: current blockers recorded with `--allow-blockers`.
- `git diff --check`: passed.

## Next

Use this chained diagnostic path on `180s` / `300s` high-pressure windows to separate three cases: opening branch helps but late filter never triggers, late filter triggers but cannot convert, or late filter triggers and creates new no-regression blockers.
