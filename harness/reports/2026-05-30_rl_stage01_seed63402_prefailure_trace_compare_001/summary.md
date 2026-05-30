# Stage 01 Seed 63402 Pre-Failure Trace Compare

- Decision: `prefailure_trace_diagnostic_recorded`
- Target: `soda-creek:63402`
- Compared traces: parent, seed-replay candidate, guard-retention probe
- Duration: `60s`

## Results

| Check | Result |
|---|---|
| Trace groups | `guard_retention_probe`, `parent`, `seed_replay_candidate` |
| Trace count | `9` |
| Target outcome | all three target traces end in defeat around `37.2664s-37.4998s` |
| Missing success actions | action `3` and action `7` |
| Excess target actions | action `4` and action `5` |
| Guard-retention target action mix | action `5` = `70.18%`, action `2` = `18.42%`, action `4` = `11.40%`, action `7` = `0.0%` |
| First high-pressure target frame | guard-retention probe: `32.3332s`, action `5` |
| Exported pre-failure states | `48` sampled high-pressure states from three failed target traces |
| Export action distribution | action `5` = `48/48` |
| Dry-run | `dataset_validated_not_training_gate`, `observation_len = 145`, `action_count = 9` |

## Conclusion

The guard-retention probe did not create a new route; it preserves the same failure shape as the parent and seed-replay candidate. Seed `63402` reaches the boundary under high enemy pressure, locks into action `5`, misses the successful same-map escape actions `3` and `7`, and dies before the 60 second window.

The exported `seed63402_prefailure_route_states.jsonl` is diagnostic input, not a training target to imitate. It should be used to design explicit target overrides, counterfactual labels, or a staged branch around the `31.9999s-37.5s` pressure window, then retested with anchor guard and target-seed preflight before any full matrix run.

## Validation

- `trace_comparison.json`: `policy_episode_trace_comparison_recorded`.
- `prefailure_route_export.json`: `policy_trace_samples_exported`.
- `prefailure_route_behavior_clone_dry_run.json`: `dataset_validated_not_training_gate`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
