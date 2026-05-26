# Runtime Surface Contract Validation

- Source: `harness/runtime_contract/runtime_surface_contract_v0.json`
- Contract: `runtime-surface-v0`
- Ruleset: `prototype-v0`
- Decision: `runtime_surface_contract_valid`
- Source files: 1
- Structs: 6
- Enums: 2
- Key bindings: 7

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks Rust source shape only; it does not compile or execute Bevy Runtime.
- It cannot prove keyboard behavior, rendered UI, platform path resolution, save migration, or upload transport behavior.
- Recovering local binary launch remains required before Runtime smoke and manual playtest can prove docs/16 and docs/18 complete.
