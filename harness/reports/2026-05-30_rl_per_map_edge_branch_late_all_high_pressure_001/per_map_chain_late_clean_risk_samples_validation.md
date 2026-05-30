# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `784`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `180.0762` to `297.5156` seconds

## Original Actions
- `1`: 72
- `2`: 41
- `3`: 97
- `4`: 112
- `5`: 95
- `6`: 113
- `7`: 100
- `8`: 154

## Target Actions
- `0`: 11
- `1`: 101
- `2`: 46
- `3`: 90
- `4`: 127
- `5`: 89
- `6`: 37
- `7`: 163
- `8`: 120

## Risk Reasons
- `toward_enemy_pressure`: 358
- `wallward_edge`: 219
- `toward_hazard`: 207
- `toward_boss`: 40

## Target Risk Reasons
- `<none>`: 784

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
