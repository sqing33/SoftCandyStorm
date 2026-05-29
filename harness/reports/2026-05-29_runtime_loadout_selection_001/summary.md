# Runtime Loadout Selection

- Decision: `runtime_loadout_selection_valid`
- Scope: `game_runtime` F5 patrol loadout selection

## Implemented

- `--character-id` selects the startup character.
- Runtime now builds `RunConfig` from the selected character and that character's initial loadout in the active content pack.
- `F5` opens a patrol preparation panel with the selected character, selected map, starting loadout, and unlocked character/map lists.
- `C` cycles unlocked characters and restarts the current patrol.
- `M` cycles unlocked maps and restarts the current patrol.

## Verification

- `cargo fmt --check`: passed
- `cargo test -p game_runtime`: 61 passed
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- Runtime surface contract refreshed at `harness/reports/2026-05-29_runtime_surface_contract_loadout_selection_001/summary.md` with decision `runtime_surface_contract_valid`

## Limitations

- This is a keyboard/text Runtime selection prototype, not the final visual base UI.
- It does not replace mouse/touch UI, accessibility, manual base UI review, or Release Candidate readiness.
- Selection only cycles content already unlocked in `MetaProgress`.
