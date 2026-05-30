# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `727`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `180.0762` to `297.149` seconds

## Original Actions
- `1`: 72
- `2`: 43
- `3`: 80
- `4`: 92
- `5`: 82
- `6`: 109
- `7`: 103
- `8`: 146

## Target Actions
- `0`: 10
- `1`: 103
- `2`: 44
- `3`: 76
- `4`: 103
- `5`: 80
- `6`: 36
- `7`: 161
- `8`: 114

## Risk Reasons
- `toward_enemy_pressure`: 304
- `wallward_edge`: 218
- `toward_hazard`: 207
- `toward_boss`: 36

## Target Risk Reasons
- `<none>`: 727

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
