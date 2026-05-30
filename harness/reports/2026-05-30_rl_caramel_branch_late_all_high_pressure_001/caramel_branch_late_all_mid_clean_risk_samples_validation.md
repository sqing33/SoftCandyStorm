# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `1139`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `178.9426` seconds

## Original Actions
- `1`: 103
- `2`: 61
- `3`: 117
- `4`: 87
- `5`: 192
- `6`: 311
- `7`: 129
- `8`: 139

## Target Actions
- `0`: 36
- `1`: 126
- `2`: 39
- `3`: 110
- `4`: 180
- `5`: 126
- `6`: 47
- `7`: 413
- `8`: 62

## Risk Reasons
- `toward_enemy_pressure`: 551
- `wallward_edge`: 524
- `toward_hazard`: 75

## Target Risk Reasons
- `<none>`: 1139

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
