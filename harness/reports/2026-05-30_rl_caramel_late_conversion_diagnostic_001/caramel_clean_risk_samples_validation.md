# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `2`
- Samples: `258`
- Maps: `caramel-workshop`
- Seeds: `63400, 63401`
- Time range: `60.0328` to `235.1213` seconds

## Original Actions
- `1`: 28
- `2`: 5
- `3`: 30
- `4`: 41
- `5`: 32
- `6`: 39
- `7`: 24
- `8`: 59

## Target Actions
- `0`: 9
- `1`: 49
- `2`: 6
- `3`: 17
- `4`: 45
- `5`: 43
- `6`: 4
- `7`: 62
- `8`: 23

## Risk Reasons
- `wallward_edge`: 139
- `toward_enemy_pressure`: 70
- `toward_hazard`: 49
- `toward_boss`: 3

## Target Risk Reasons
- `<none>`: 258

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
