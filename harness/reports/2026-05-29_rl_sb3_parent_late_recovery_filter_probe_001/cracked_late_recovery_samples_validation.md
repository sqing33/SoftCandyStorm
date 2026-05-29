# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `223`
- Maps: `cracked-star-jar`
- Seeds: `63101, 63102`
- Time range: `180.0095` to `284.1522` seconds

## Original Actions
- `1`: 25
- `2`: 4
- `3`: 28
- `4`: 42
- `5`: 20
- `6`: 47
- `7`: 12
- `8`: 45

## Target Actions
- `0`: 7
- `1`: 32
- `2`: 5
- `3`: 17
- `4`: 49
- `5`: 14
- `6`: 19
- `7`: 47
- `8`: 33

## Risk Reasons
- `toward_enemy_pressure`: 98
- `wallward_edge`: 74
- `toward_hazard`: 66
- `toward_boss`: 2

## Target Risk Reasons
- `<none>`: 210
- `toward_enemy_pressure`: 7
- `idle_under_late_pressure`: 6

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
