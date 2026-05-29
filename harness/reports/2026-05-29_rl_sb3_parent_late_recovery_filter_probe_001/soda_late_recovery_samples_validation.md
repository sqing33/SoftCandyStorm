# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `123`
- Maps: `soda-creek`
- Seeds: `63100, 63102`
- Time range: `180.0095` to `299.8817` seconds

## Original Actions
- `1`: 12
- `2`: 3
- `3`: 15
- `4`: 15
- `5`: 12
- `6`: 29
- `7`: 11
- `8`: 26

## Target Actions
- `0`: 6
- `1`: 6
- `2`: 3
- `3`: 17
- `4`: 22
- `5`: 34
- `6`: 3
- `7`: 12
- `8`: 20

## Risk Reasons
- `toward_enemy_pressure`: 67
- `wallward_edge`: 60
- `toward_boss`: 2
- `toward_hazard`: 1

## Target Risk Reasons
- `<none>`: 122
- `toward_boss`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/soda-creek_edge_recovery_samples.jsonl:113 seed 63102 map soda-creek: target risk score 0.239835 is worse than original 0.200243
