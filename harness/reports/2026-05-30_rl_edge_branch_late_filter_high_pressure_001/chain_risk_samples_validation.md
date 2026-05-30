# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `6`
- Samples: `2000`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `297.5156` seconds

## Original Actions
- `1`: 167
- `2`: 68
- `3`: 219
- `4`: 187
- `5`: 341
- `6`: 488
- `7`: 231
- `8`: 299

## Target Actions
- `0`: 53
- `1`: 202
- `2`: 70
- `3`: 192
- `4`: 378
- `5`: 203
- `6`: 61
- `7`: 648
- `8`: 193

## Risk Reasons
- `toward_enemy_pressure`: 953
- `wallward_edge`: 803
- `toward_hazard`: 252
- `toward_boss`: 42

## Target Risk Reasons
- `<none>`: 1967
- `toward_enemy_pressure`: 13
- `toward_boss`: 11
- `idle_under_late_pressure`: 8
- `toward_hazard`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl:93 seed 63401 map caramel-workshop: target risk score 0.103595 is worse than original 0.040605
- harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl:94 seed 63401 map caramel-workshop: target risk score 0.113089 is worse than original 0.031317
- harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl:95 seed 63401 map caramel-workshop: target risk score 0.118338 is worse than original 0.02852
- harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_soda-creek_risk_only.jsonl:184 seed 63400 map soda-creek: target risk score 0.066986 is worse than original 0.019223
- harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl:69 seed 63400 map caramel-workshop: target risk score 0.31294 is worse than original 0.121505
- harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_cracked-star-jar.jsonl:78 seed 63400 map cracked-star-jar: target risk score 0.046002 is worse than original 0.028885
