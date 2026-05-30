# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `164`
- Maps: `caramel-workshop`
- Seeds: `63400, 63401, 63402`
- Time range: `180.0762` to `243.7898` seconds

## Original Actions
- `1`: 18
- `2`: 2
- `3`: 17
- `4`: 31
- `5`: 16
- `6`: 32
- `7`: 10
- `8`: 38

## Target Actions
- `0`: 3
- `1`: 38
- `2`: 3
- `3`: 10
- `4`: 17
- `5`: 33
- `6`: 6
- `7`: 42
- `8`: 12

## Risk Reasons
- `wallward_edge`: 102
- `toward_hazard`: 54
- `toward_enemy_pressure`: 7
- `toward_boss`: 3

## Target Risk Reasons
- `<none>`: 164

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
