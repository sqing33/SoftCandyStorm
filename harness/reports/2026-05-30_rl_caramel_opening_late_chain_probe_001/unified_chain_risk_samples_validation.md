# Risk Recovery Sample Validation

- Decision: `risk_recovery_samples_valid`
- Sources: `1`
- Samples: `2165`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `60.0328` to `297.149` seconds

## Original Actions
- `1`: 197
- `2`: 103
- `3`: 216
- `4`: 220
- `5`: 301
- `6`: 563
- `7`: 246
- `8`: 319

## Target Actions
- `0`: 55
- `1`: 256
- `2`: 80
- `3`: 205
- `4`: 312
- `5`: 241
- `6`: 80
- `7`: 740
- `8`: 196

## Risk Reasons
- `toward_enemy_pressure`: 945
- `wallward_edge`: 930
- `toward_hazard`: 301
- `toward_boss`: 39

## Target Risk Reasons
- `<none>`: 2137
- `toward_enemy_pressure`: 13
- `toward_boss`: 9
- `idle_under_late_pressure`: 5
- `toward_hazard`: 1

## Notes
- This validator checks sample structure and late-risk reason consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.

## Warnings
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:93 seed 63401 map caramel-workshop: target risk score 0.103595 is worse than original 0.040605
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:94 seed 63401 map caramel-workshop: target risk score 0.113089 is worse than original 0.031317
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:95 seed 63401 map caramel-workshop: target risk score 0.118338 is worse than original 0.02852
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:808 seed 63400 map caramel-workshop: target risk score 0.31294 is worse than original 0.121505
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:1026 seed 63402 map caramel-workshop: target risk score 0.115372 is worse than original 0.106327
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:1190 seed 63400 map cracked-star-jar: target risk score 0.046002 is worse than original 0.028885
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:1730 seed 63400 map soda-creek: target risk score 0.015503 is worse than original 0.009675
- harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl:1778 seed 63400 map soda-creek: target risk score 0.12117 is worse than original 0.042036
