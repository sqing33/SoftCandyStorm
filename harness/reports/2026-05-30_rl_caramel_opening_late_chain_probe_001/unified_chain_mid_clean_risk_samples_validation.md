# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `1402`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `179.8428` seconds

## Original Actions
- `1`: 122
- `2`: 57
- `3`: 127
- `4`: 126
- `5`: 212
- `6`: 452
- `7`: 140
- `8`: 166

## Target Actions
- `0`: 40
- `1`: 150
- `2`: 33
- `3`: 125
- `4`: 206
- `5`: 158
- `6`: 44
- `7`: 566
- `8`: 80

## Risk Reasons
- `wallward_edge`: 711
- `toward_enemy_pressure`: 628
- `toward_hazard`: 75

## Target Risk Reasons
- `<none>`: 1402

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
