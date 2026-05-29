# Runtime Codex Browsing

- Decision: `runtime_codex_browsing_valid`
- Scope: `game_runtime` F3 codex category and entry browsing

## Implemented

- F3 now renders a browseable codex entry detail area in addition to discovered-count summaries.
- `Q/E` cycle categories across characters, weapons, passives, enemies, Bosses, maps, evolutions, and events.
- `B/N` cycle visible entries in the selected category.
- `V` toggles discovered-only versus all-entry filtering.
- Locked entries redact name and description and show a safe locked-state prompt.
- F3 category/filter state and F1-F5 selected panel state persist through save-state-v1 `base_ui_state` when the user changes codex controls or switches station panels.
- Runtime startup restores the saved F1-F5 selected panel key, falling back to overview for unknown values.

## Verification

- `cargo test -p game_runtime`: 65 passed
- `cargo test --workspace`: 130 passed
- `cargo clippy --workspace --all-targets`: passed
- `cargo fmt --check`: passed
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- Runtime surface contract refreshed at `harness/reports/2026-05-29_runtime_surface_contract_codex_browsing_001/summary.md` with decision `runtime_surface_contract_valid`

## Limitations

- This is a keyboard/text Runtime codex prototype, not the final visual base UI.
- It reads accepted runtime content pack metadata and `MetaProgress` only; it does not load generated story/codex candidate text.
- It does not replace human story review, Runtime UI review, final human acceptance, manual base UI review, or release readiness.
