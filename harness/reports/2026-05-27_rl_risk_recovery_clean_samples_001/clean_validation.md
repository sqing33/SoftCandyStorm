# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `702`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `180.0095` to `297.6156` seconds

## Original Actions
- `1`: 80
- `2`: 109
- `3`: 91
- `4`: 93
- `5`: 61
- `6`: 119
- `7`: 81
- `8`: 68

## Target Actions
- `1`: 72
- `2`: 59
- `3`: 144
- `4`: 77
- `5`: 147
- `6`: 36
- `7`: 94
- `8`: 73

## Risk Reasons
- `toward_enemy_pressure`: 368
- `toward_hazard`: 169
- `wallward_edge`: 147
- `toward_boss`: 59

## Target Risk Reasons
- `<none>`: 702

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
