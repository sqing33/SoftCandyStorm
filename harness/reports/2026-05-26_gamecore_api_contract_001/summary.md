# GameCore API Contract Validation

- Source: `harness/interface_contract/gamecore_api_contract_v0.json`
- Contract: `gamecore-api-v0`
- Ruleset: `prototype-v0`
- Decision: `gamecore_api_contract_valid`
- Source files: 4
- Structs: 20
- Enums: 5

## Errors

- None

## Warnings

- None

## Known Gaps

- Count: 3

## Limitations

- This validator checks Rust source shape only; it does not compile or execute GameCore.
- It cannot prove deterministic semantics, replay compatibility, runtime integration, or Gym behavior.
- Recovering local binary launch remains required before cargo test and Harness validation can prove docs/14 complete.
