# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `440`
- Maps: `caramel-workshop`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `178.2091` seconds

## Original Actions
- `1`: 37
- `2`: 6
- `3`: 44
- `4`: 59
- `5`: 84
- `6`: 89
- `7`: 51
- `8`: 70

## Target Actions
- `0`: 15
- `1`: 42
- `2`: 7
- `3`: 38
- `4`: 93
- `5`: 67
- `6`: 12
- `7`: 135
- `8`: 31

## Risk Reasons
- `wallward_edge`: 202
- `toward_enemy_pressure`: 172
- `toward_hazard`: 75

## Target Risk Reasons
- `<none>`: 440

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
