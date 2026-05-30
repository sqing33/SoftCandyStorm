# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `634`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `180.0762` to `299.2818` seconds

## Original Actions
- `1`: 66
- `2`: 30
- `3`: 65
- `4`: 88
- `5`: 67
- `6`: 83
- `7`: 90
- `8`: 145

## Target Actions
- `0`: 11
- `1`: 95
- `2`: 33
- `3`: 63
- `4`: 98
- `5`: 67
- `6`: 31
- `7`: 132
- `8`: 104

## Risk Reasons
- `toward_enemy_pressure`: 248
- `toward_hazard`: 208
- `wallward_edge`: 188
- `toward_boss`: 30

## Target Risk Reasons
- `<none>`: 634

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
