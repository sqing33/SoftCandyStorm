# Runtime F4 Local Data Controls

- Decision: `runtime_f4_local_data_controls_valid`
- Scope: `game_runtime` F4 privacy settings local data controls

## Implemented

- `E` exports the current Runtime save to `exports/profile_export.json`.
- `X` deletes the configured Runtime save through the existing explicit save deletion guard.
- `L` exports configured local telemetry / replay / crash data to `exports/local_data_export.json`.
- `K` deletes configured local telemetry / replay / crash data through the existing explicit local directory guard.
- The F4 settings panel now names the E/X/L/K entries and the `exports/` destination.

## Verification

- `cargo fmt --check`: passed
- `cargo test -p game_runtime`: 59 passed
- Runtime surface contract refreshed at `harness/reports/2026-05-29_runtime_surface_contract_f4_local_data_controls_001/summary.md` with decision `runtime_surface_contract_valid`
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed

## Limitations

- This is not native platform storage validation.
- This is not manual privacy, platform path, legal, base UI, or release candidate approval.
- These are keyboard Runtime entries, not final release-grade UI buttons.
