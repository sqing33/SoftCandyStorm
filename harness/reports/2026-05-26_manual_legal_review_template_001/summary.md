# Manual Legal Review Validation

- Source: `harness/telemetry_privacy/manual_legal_review_template.json`
- Decision: `manual_legal_review_invalid`
- Gate decision: `needs_more_review`
- Jurisdiction scope: `TODO: prototype_local | steam_pc | cn | global`
- Checks: 9
- Issues: 9
- Global risks: 1
- Policy: `telemetry_privacy_policy_valid`
- Runtime privacy contract: `runtime_privacy_settings_contract_valid`
- Upload transport contract: `upload_transport_contract_valid`
- Manual privacy review: `None`
- Manual platform path review: `None`

## Errors

- review_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- reviewer_role must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- jurisdiction_scope must contain only concrete strings
- manual_privacy_review_report must not contain TODO or placeholder markers
- manual_platform_path_review_report must not contain TODO or placeholder markers
- manual_privacy_review_report decision must be `manual_privacy_review_valid`
- manual_platform_path_review_report decision must be `manual_platform_path_review_valid`
- privacy_notice_claims: notes must not contain TODO or placeholder markers
- privacy_notice_claims: required_changes must not contain TODO or placeholder markers
- consent_and_default_off: notes must not contain TODO or placeholder markers
- consent_and_default_off: required_changes must not contain TODO or placeholder markers
- prohibited_data_fields: notes must not contain TODO or placeholder markers
- prohibited_data_fields: required_changes must not contain TODO or placeholder markers
- raw_replay_and_crash_reports: notes must not contain TODO or placeholder markers
- raw_replay_and_crash_reports: required_changes must not contain TODO or placeholder markers
- retention_delete_export: notes must not contain TODO or placeholder markers
- retention_delete_export: required_changes must not contain TODO or placeholder markers
- platform_path_and_local_data_scope: notes must not contain TODO or placeholder markers
- platform_path_and_local_data_scope: required_changes must not contain TODO or placeholder markers
- upload_transport_status: notes must not contain TODO or placeholder markers
- upload_transport_status: required_changes must not contain TODO or placeholder markers
- jurisdiction_and_store_requirements: notes must not contain TODO or placeholder markers
- jurisdiction_and_store_requirements: required_changes must not contain TODO or placeholder markers
- release_evidence_limits: notes must not contain TODO or placeholder markers
- release_evidence_limits: required_changes must not contain TODO or placeholder markers
- global_risks must not contain TODO or placeholder markers
- next_actions must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks manual legal/compliance review record completeness only.
- It does not provide legal advice, platform approval, or release readiness.
- A pass gate still requires executable Runtime evidence and Release Candidate gates.
