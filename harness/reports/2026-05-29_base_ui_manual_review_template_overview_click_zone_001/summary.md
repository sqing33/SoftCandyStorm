# Base UI Manual Review Validation

- Source: `harness/save_contract/base_ui_manual_review_template.json`
- Decision: `base_ui_manual_review_invalid`
- Review id: `<base-ui-manual-review-id>`
- Gate decision: `needs_more_review`
- Runtime surface contract: `runtime_surface_contract_valid`
- Save state contract: `save_state_contract_valid`
- Checks: 8
- Issue checks: 8
- Global risks: 1
- Next actions: 1

## Errors

- review_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- runtime_surface_validation_report does not exist: harness/reports/2026-05-29_runtime_surface_contract_overview_click_zone_001/summary.md
- overview_panel: notes must not contain TODO or placeholder markers
- overview_panel: required_changes must not contain TODO or placeholder markers
- chapter_navigation: notes must not contain TODO or placeholder markers
- chapter_navigation: required_changes must not contain TODO or placeholder markers
- character_map_selection: notes must not contain TODO or placeholder markers
- character_map_selection: required_changes must not contain TODO or placeholder markers
- codex_navigation: notes must not contain TODO or placeholder markers
- codex_navigation: required_changes must not contain TODO or placeholder markers
- privacy_settings_access: notes must not contain TODO or placeholder markers
- privacy_settings_access: required_changes must not contain TODO or placeholder markers
- local_data_controls: notes must not contain TODO or placeholder markers
- local_data_controls: required_changes must not contain TODO or placeholder markers
- candidate_content_boundaries: notes must not contain TODO or placeholder markers
- candidate_content_boundaries: required_changes must not contain TODO or placeholder markers
- runtime_evidence_limits: notes must not contain TODO or placeholder markers
- runtime_evidence_limits: required_changes must not contain TODO or placeholder markers
- global_risks must not contain TODO or placeholder markers
- next_actions must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks manual base UI review record completeness only.
- It does not run Bevy, inspect screenshots, certify UX quality, integrate candidates, or approve release readiness.
- A valid base UI manual review does not replace manual playtest, privacy, platform path, content, or asset acceptance gates.
