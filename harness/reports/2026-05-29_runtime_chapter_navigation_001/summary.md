# Runtime Chapter Navigation

- Decision: `runtime_chapter_navigation_valid`
- Scope: `game_runtime` F2 chapter target selection and unlocked-chapter start affordance

## Implemented

- F2 now renders a selected chapter with map, Boss, goal checklist, unlock state, and latest run settlement context.
- `Q/E` cycle the selected chapter through the `MetaProgress` chapter roster.
- Chapter selection persists through save-state-v1 `base_ui_state.last_selected_chapter_id` when a save file is configured.
- `G` starts a new patrol on the selected chapter map only when that chapter is unlocked.
- Locked chapters render a blocking message, and `G` refuses to launch unavailable content.
- First-chapter goals render as checklist rows; future chapter goals stay gated until accepted content and balance validation exist.

## Verification

- `cargo test -p game_runtime`: 67 passed
- `cargo test --workspace`: 132 passed
- `cargo clippy --workspace --all-targets`: passed
- `cargo fmt --check`: passed
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- `python3 tools/test_validate_base_ui_manual_review.py`: 7 passed
- Runtime surface contract refreshed at `harness/reports/2026-05-29_runtime_surface_contract_chapter_navigation_001/summary.md` with decision `runtime_surface_contract_valid`
- Base UI manual review template refreshed at `harness/reports/2026-05-29_base_ui_manual_review_template_chapter_navigation_001/summary.md` with expected decision `base_ui_manual_review_invalid`

## Limitations

- This is a keyboard/text Runtime chapter-navigation prototype, not the final visual base UI.
- Future chapter goal definitions still require accepted content and balance validation.
- The base UI manual review template remains invalid until a human reviewer replaces placeholders and records a real decision.
- This does not replace human base UI review, manual playtest, platform path review, final content acceptance, or release readiness.
