# Manual Privacy Review Validation

- Source: `harness/telemetry_privacy/manual_privacy_review_template.json`
- Decision: `manual_privacy_review_invalid`
- Gate decision: `needs_more_review`
- Checks reviewed: 8 / 8
- Repair checks: 8
- Global risks: 1

## Errors

- review_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- default_off: notes must not contain TODO or placeholder markers
- default_off: required_changes must not contain TODO or placeholder markers
- explicit_consent: notes must not contain TODO or placeholder markers
- explicit_consent: required_changes must not contain TODO or placeholder markers
- raw_replay_separate_consent: notes must not contain TODO or placeholder markers
- raw_replay_separate_consent: required_changes must not contain TODO or placeholder markers
- prohibited_fields: notes must not contain TODO or placeholder markers
- prohibited_fields: required_changes must not contain TODO or placeholder markers
- delete_export_controls: notes must not contain TODO or placeholder markers
- delete_export_controls: required_changes must not contain TODO or placeholder markers
- privacy_notice_text: notes must not contain TODO or placeholder markers
- privacy_notice_text: required_changes must not contain TODO or placeholder markers
- retention_and_storage: notes must not contain TODO or placeholder markers
- retention_and_storage: required_changes must not contain TODO or placeholder markers
- runtime_evidence_limits: notes must not contain TODO or placeholder markers
- runtime_evidence_limits: required_changes must not contain TODO or placeholder markers
- global_risks must not contain TODO or placeholder markers
- next_actions must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks manual privacy review completeness only.
- It does not provide legal advice or platform compliance approval.
- A pass decision does not prove upload transport, executable Runtime behavior, or release readiness.
