# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `373`
- Maps: `caramel-workshop`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `243.7898` seconds

## Original Actions
- `1`: 34
- `2`: 4
- `3`: 38
- `4`: 43
- `5`: 65
- `6`: 79
- `7`: 36
- `8`: 74

## Target Actions
- `0`: 9
- `1`: 59
- `2`: 6
- `3`: 30
- `4`: 71
- `5`: 52
- `6`: 10
- `7`: 113
- `8`: 23

## Risk Reasons
- `wallward_edge`: 185
- `toward_hazard`: 103
- `toward_enemy_pressure`: 90
- `toward_boss`: 3

## Target Risk Reasons
- `<none>`: 373

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl:69 seed 63400 map caramel-workshop: target risk score 0.31294 is worse than original 0.121505
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl:287 seed 63402 map caramel-workshop: target risk score 0.115372 is worse than original 0.106327
