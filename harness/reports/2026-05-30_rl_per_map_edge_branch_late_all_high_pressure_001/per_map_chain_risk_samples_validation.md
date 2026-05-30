# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `2184`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `297.5156` seconds

## Original Actions
- `1`: 185
- `2`: 69
- `3`: 238
- `4`: 226
- `5`: 370
- `6`: 525
- `7`: 251
- `8`: 320

## Target Actions
- `0`: 58
- `1`: 219
- `2`: 72
- `3`: 210
- `4`: 397
- `5`: 250
- `6`: 72
- `7`: 702
- `8`: 204

## Risk Reasons
- `toward_enemy_pressure`: 995
- `wallward_edge`: 900
- `toward_hazard`: 301
- `toward_boss`: 42

## Target Risk Reasons
- `<none>`: 2151
- `toward_enemy_pressure`: 13
- `toward_boss`: 11
- `idle_under_late_pressure`: 8
- `toward_hazard`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:93 seed 63401 map caramel-workshop: target risk score 0.103595 is worse than original 0.040605
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:94 seed 63401 map caramel-workshop: target risk score 0.113089 is worse than original 0.031317
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:95 seed 63401 map caramel-workshop: target risk score 0.118338 is worse than original 0.02852
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:822 seed 63400 map caramel-workshop: target risk score 0.31294 is worse than original 0.121505
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:1040 seed 63402 map caramel-workshop: target risk score 0.115372 is worse than original 0.106327
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:1204 seed 63400 map cracked-star-jar: target risk score 0.046002 is worse than original 0.028885
- harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl:1798 seed 63400 map soda-creek: target risk score 0.066986 is worse than original 0.019223
