# Runtime Surface Contract Validation

- Source: `harness/runtime_contract/runtime_surface_contract_v0.json`
- Contract: `runtime-surface-v0`
- Ruleset: `prototype-v0`
- Decision: `runtime_surface_contract_valid`
- Source files: 1
- Structs: 20
- Enums: 7
- Key bindings: 37

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks Rust source shape only; it does not compile or execute Bevy Runtime.
- It cannot prove keyboard behavior, rendered UI, platform path resolution, save migration, or upload transport behavior.
- Runtime smoke, platform path review, and manual playtest remain required before docs/16 and docs/18 can be marked complete.
