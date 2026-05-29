# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `3`
- Samples: `439`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63100, 63101, 63102`
- Time range: `180.0095` to `299.8817` seconds

## Original Actions
- `1`: 45
- `2`: 15
- `3`: 52
- `4`: 62
- `5`: 44
- `6`: 82
- `7`: 45
- `8`: 94

## Target Actions
- `0`: 16
- `1`: 53
- `2`: 13
- `3`: 43
- `4`: 79
- `5`: 56
- `6`: 27
- `7`: 79
- `8`: 73

## Risk Reasons
- `wallward_edge`: 173
- `toward_enemy_pressure`: 169
- `toward_hazard`: 124
- `toward_boss`: 6

## Target Risk Reasons
- `<none>`: 425
- `toward_enemy_pressure`: 7
- `idle_under_late_pressure`: 6
- `toward_boss`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/soda-creek_edge_recovery_samples.jsonl:113 seed 63102 map soda-creek: target risk score 0.239835 is worse than original 0.200243
