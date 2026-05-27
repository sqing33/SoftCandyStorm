# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `3`
- Samples: `780`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `180.0095` to `297.6156` seconds

## Original Actions
- `1`: 83
- `2`: 116
- `3`: 105
- `4`: 103
- `5`: 64
- `6`: 125
- `7`: 83
- `8`: 101

## Target Actions
- `0`: 32
- `1`: 79
- `2`: 63
- `3`: 144
- `4`: 89
- `5`: 147
- `6`: 46
- `7`: 101
- `8`: 79

## Risk Reasons
- `toward_enemy_pressure`: 422
- `toward_hazard`: 185
- `wallward_edge`: 158
- `toward_boss`: 65

## Target Risk Reasons
- `<none>`: 707
- `idle_under_late_pressure`: 32
- `toward_boss`: 19
- `toward_enemy_pressure`: 19
- `toward_hazard`: 3

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl:173 seed 62402 map soda-creek: target risk score 0.087046 is worse than original 0.073857
- harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl:174 seed 62402 map soda-creek: target risk score 0.096775 is worse than original 0.057893
- harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_cracked-star-jar.jsonl:99 seed 62400 map cracked-star-jar: target risk score 0.156885 is worse than original 0.043881
- harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_cracked-star-jar.jsonl:202 seed 62402 map cracked-star-jar: target risk score 0.041685 is worse than original 0.038013
- harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_cracked-star-jar.jsonl:249 seed 62402 map cracked-star-jar: target risk score 0.042447 is worse than original 0.016203
