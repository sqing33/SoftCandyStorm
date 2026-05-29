# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `424`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63100, 63101, 63102`
- Time range: `180.0095` to `299.8817` seconds

## Original Actions
- `1`: 45
- `2`: 14
- `3`: 46
- `4`: 62
- `5`: 43
- `6`: 80
- `7`: 45
- `8`: 89

## Target Actions
- `0`: 10
- `1`: 52
- `2`: 13
- `3`: 43
- `4`: 74
- `5`: 56
- `6`: 26
- `7`: 77
- `8`: 73

## Risk Reasons
- `wallward_edge`: 168
- `toward_enemy_pressure`: 159
- `toward_hazard`: 124
- `toward_boss`: 6

## Target Risk Reasons
- `<none>`: 424

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
