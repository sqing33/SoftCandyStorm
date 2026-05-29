# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `93`
- Maps: `caramel-workshop`
- Seeds: `63100, 63102`
- Time range: `180.0095` to `233.3876` seconds

## Original Actions
- `1`: 8
- `2`: 8
- `3`: 9
- `4`: 5
- `5`: 12
- `6`: 6
- `7`: 22
- `8`: 23

## Target Actions
- `0`: 3
- `1`: 15
- `2`: 5
- `3`: 9
- `4`: 8
- `5`: 8
- `6`: 5
- `7`: 20
- `8`: 20

## Risk Reasons
- `toward_hazard`: 57
- `wallward_edge`: 39
- `toward_enemy_pressure`: 4
- `toward_boss`: 2

## Target Risk Reasons
- `<none>`: 93

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
