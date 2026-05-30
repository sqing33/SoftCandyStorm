# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `1360`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `179.8094` seconds

## Original Actions
- `1`: 111
- `2`: 23
- `3`: 130
- `4`: 112
- `5`: 268
- `6`: 410
- `7`: 148
- `8`: 158

## Target Actions
- `0`: 39
- `1`: 115
- `2`: 23
- `3`: 114
- `4`: 267
- `5`: 158
- `6`: 35
- `7`: 527
- `8`: 82

## Risk Reasons
- `wallward_edge`: 678
- `toward_enemy_pressure`: 619
- `toward_hazard`: 75

## Target Risk Reasons
- `<none>`: 1360

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
