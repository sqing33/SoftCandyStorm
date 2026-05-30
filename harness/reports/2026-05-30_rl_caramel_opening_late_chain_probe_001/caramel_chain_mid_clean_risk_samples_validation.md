# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `207`
- Maps: `caramel-workshop`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `177.3756` seconds

## Original Actions
- `1`: 15
- `2`: 2
- `3`: 21
- `4`: 12
- `5`: 49
- `6`: 46
- `7`: 26
- `8`: 36

## Target Actions
- `0`: 6
- `1`: 21
- `2`: 3
- `3`: 20
- `4`: 54
- `5`: 18
- `6`: 4
- `7`: 70
- `8`: 11

## Risk Reasons
- `wallward_edge`: 83
- `toward_enemy_pressure`: 81
- `toward_hazard`: 49

## Target Risk Reasons
- `<none>`: 207

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
