# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `1806`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `299.2818` seconds

## Original Actions
- `1`: 171
- `2`: 94
- `3`: 191
- `4`: 177
- `5`: 265
- `6`: 396
- `7`: 222
- `8`: 290

## Target Actions
- `0`: 52
- `1`: 223
- `2`: 74
- `3`: 177
- `4`: 281
- `5`: 196
- `6`: 78
- `7`: 557
- `8`: 168

## Risk Reasons
- `toward_enemy_pressure`: 811
- `wallward_edge`: 713
- `toward_hazard`: 302
- `toward_boss`: 31

## Target Risk Reasons
- `<none>`: 1779
- `toward_enemy_pressure`: 13
- `toward_boss`: 8
- `idle_under_late_pressure`: 5
- `toward_hazard`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl:93 seed 63401 map caramel-workshop: target risk score 0.103595 is worse than original 0.040605
- harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl:94 seed 63401 map caramel-workshop: target risk score 0.113089 is worse than original 0.031317
- harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl:95 seed 63401 map caramel-workshop: target risk score 0.118338 is worse than original 0.02852
- harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl:723 seed 63400 map caramel-workshop: target risk score 0.31294 is worse than original 0.121505
- harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl:941 seed 63402 map caramel-workshop: target risk score 0.115372 is worse than original 0.106327
- harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl:1105 seed 63400 map cracked-star-jar: target risk score 0.046002 is worse than original 0.028885
