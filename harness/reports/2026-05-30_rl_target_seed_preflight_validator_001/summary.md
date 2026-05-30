# RL Target Seed Preflight Validator

- Decision: `tool_added`
- Tool: `tools/validate_policy_target_seed_preflight.py`
- Test: `tools/test_validate_policy_target_seed_preflight.py`
- Example report: `seed63402_strong_guard_preflight.json`

## Result

The validator reads an existing policy comparison report and checks selected `map_id:seed` episodes before a repair branch continues. It can require window survival, non-defeat terminal status, minimum survival seconds, and per-action ratio bounds.

The first real run used the strong guard-anchor 60 second comparison for `soda-creek:63402`:

| Check | Result |
|---|---|
| Decision | `policy_target_seed_preflight_failed` |
| Time | `45.2330s`, below the `60s` window |
| Terminal | `defeat` |
| Action `7` ratio | `0.0`, below required `0.1` |

## Conclusion

This tool gives future stage 01 repair runs a cheap online preflight before full 60 / 180 / 300 second matrix evaluation. It does not replace high-pressure comparison, parent no-regression, failure-case review, or RL acceptance; it only prevents an already-failed target seed from being hidden inside larger aggregate reports.

## Validation

- `python3 -m unittest tools/test_validate_policy_target_seed_preflight.py`: passed.
- Example preflight report generated with `--allow-failure` because the strong guard-anchor checkpoint is expected to fail this gate.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
