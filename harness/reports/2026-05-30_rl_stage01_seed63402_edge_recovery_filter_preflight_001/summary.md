# Stage 01 Seed 63402 Edge Recovery Filter Preflight

- Decision: `diagnostic_repair_signal_not_policy_gate`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Adapter: `edge_recovery_filter`
- Edge distance: `32`
- Reward profile: `opening-boundary-escape`

## Results

| Check | Result |
|---|---|
| Evaluation scope | `soda-creek`, seeds `63400-63402`, `60s` |
| Policy win rate | `1.0` |
| Average survival | `60.0328s` |
| Target seed preflight | `policy_target_seed_preflight_passed` |
| Target seed `63402` | victory at `60.0328s`, action `7` ratio `0.2965` |
| Target seed action counts | action `7` = `534`, action `5` = `365`, action `3` = `316`, action `8` = `247`, action `2` = `201` |
| Exported repair samples | `76` edge recovery supervision samples |
| Sample validation | `edge_recovery_samples_valid` |
| Behavior clone dry-run | `dataset_validated_not_training_gate` |

## Conclusion

The deterministic edge recovery filter is the first cheap probe in this seed `63402` chain to pass target preflight. It confirms that the parent policy has usable non-wallward actions in its distribution, and that the opening failure can be reframed as a deterministic edge-pushing / edge-lock problem rather than only a missing action `7` label.

This is not policy acceptance evidence because `edge_recovery_filter` is a hand-written diagnostic adapter. The useful artifact is the exported `edge_recovery_samples.jsonl`, which should be treated as repair training input for a learned or constrained seed-specific opening branch.

## Validation

- `comparison_60s.json`: `comparison_recorded_not_balance_gate` with `policy_adapter.mode = edge_recovery_filter`.
- `target_seed_preflight.json`: `policy_target_seed_preflight_passed`.
- `edge_recovery_samples_validation.json`: `edge_recovery_samples_valid`.
- `behavior_clone_dry_run.json`: `dataset_validated_not_training_gate`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
