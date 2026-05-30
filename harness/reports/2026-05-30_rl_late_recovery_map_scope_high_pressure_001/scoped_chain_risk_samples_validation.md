# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `610`
- Maps: `caramel-workshop`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `243.7898` seconds

## Original Actions
- `1`: 56
- `2`: 8
- `3`: 61
- `4`: 90
- `5`: 104
- `6`: 122
- `7`: 61
- `8`: 108

## Target Actions
- `0`: 18
- `1`: 80
- `2`: 10
- `3`: 48
- `4`: 113
- `5`: 101
- `6`: 18
- `7`: 178
- `8`: 44

## Risk Reasons
- `wallward_edge`: 304
- `toward_enemy_pressure`: 185
- `toward_hazard`: 129
- `toward_boss`: 3

## Target Risk Reasons
- `<none>`: 609
- `toward_enemy_pressure`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl:93 seed 63401 map caramel-workshop: target risk score 0.103595 is worse than original 0.040605
- harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl:94 seed 63401 map caramel-workshop: target risk score 0.113089 is worse than original 0.031317
- harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl:95 seed 63401 map caramel-workshop: target risk score 0.118338 is worse than original 0.02852
- harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl:306 seed 63400 map caramel-workshop: target risk score 0.31294 is worse than original 0.121505
- harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl:524 seed 63402 map caramel-workshop: target risk score 0.115372 is worse than original 0.106327
