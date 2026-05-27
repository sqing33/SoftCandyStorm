# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `9`
- Inspected trace rows: `966`
- Negative route_recovery rows: `735`
- Boundary hotspot rows: `721`
- Missing observation rows: `0`
- Exported samples: `689`
- Samples: `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 188, "cracked-star-jar": 279, "soda-creek": 222}`
- Original actions: `{"3": 137, "4": 397, "7": 155}`
- Target actions: `{"1": 47, "2": 151, "3": 103, "5": 61, "7": 5, "8": 322}`
- Target labels: `{"geometry_inward_non_wallward_action": 478, "highest_scored_non_wallward_action": 211}`

## Validation

- Edge sample validation: `edge_recovery_samples_valid`
- Validation report: `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/route_recovery_samples_validation.json`
- Behavior clone dry-run: `dataset_validated_not_training_gate`
- Dry-run report: `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/behavior_clone_dry_run.json`
- Dry-run sample count: `689`
- Dry-run health ratio min / average: `0.2867 / 0.7399`

## Source Evaluations

- Model: `harness/reports/2026-05-27_rl_route_recovery_reward_profile_smoke_001/ppo_route_recovery_reward_profile_smoke.zip`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Reward profile: `long-run-retention`
- Evaluation: deterministic 300-second high-pressure failed-only traces, seeds `62300-62302`
- Win rate: `0%` on `soda-creek`, `caramel-workshop`, and `cracked-star-jar`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
