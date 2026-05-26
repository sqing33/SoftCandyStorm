# Manual Legal Review Packet

- Review template: `harness/telemetry_privacy/manual_legal_review_template.json`
- Gate decision: `needs_more_review`
- Summary status: `draft_todo`
- Reviewer status: `draft_todo`
- Jurisdiction status: `draft_todo`
- Checks: 9
- Draft TODO checks: 9

## Bound Evidence

- Policy: `harness/telemetry_privacy/telemetry_privacy_policy_template.json`
- Runtime privacy contract: `harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json`
- Save contract: `harness/save_contract/save_state_v0_template.json`
- Upload transport contract: `harness/telemetry_privacy/upload_transport_contract_v0.json`

## Report References

| Report | Path | Status | Decision |
|---|---|---|---|
| `policy_validation_report` | `harness/reports/2026-05-26_telemetry_privacy_policy_001/summary.md` | `present` | `` |
| `runtime_contract_validation_report` | `harness/reports/2026-05-26_runtime_privacy_settings_contract_001/summary.md` | `present` | `` |
| `upload_transport_validation_report` | `harness/reports/2026-05-26_upload_transport_contract_001/summary.md` | `present` | `` |
| `manual_privacy_review_report` | `harness/reports/<manual-privacy-review>/manual_privacy_review.json` | `draft_placeholder` | `` |
| `manual_platform_path_review_report` | `harness/reports/<manual-platform-path-review>/manual_platform_path_review.json` | `draft_placeholder` | `` |

## Jurisdiction Scope

- `TODO: prototype_local | steam_pc | cn | global`

## Privacy And Upload Summary

- Policy id: `local-first-telemetry-privacy-v001`
- Policy scope: `development-local`
- Upload enabled: `False`
- Upload default enabled: `False`
- Upload requires consent: `True`
- Raw replay default enabled: `False`
- Raw replay requires consent: `True`
- Crash report default enabled: `False`
- Crash report requires consent: `True`
- Retention days: `30`
- Runtime contract id: `runtime-privacy-settings-v0`
- Save contract id: `save-state-v0`
- Upload contract id: `telemetry-upload-transport-v0`
- Upload implementation status: `planned`
- Upload transport mode: `None`

## Prohibited Fields

- `personal_identity`
- `email`
- `ip_address`
- `file_path`
- `free_text_input`
- `raw_replay_action_stream`

## Upload Release Requirements

- `telemetry_privacy_policy`
- `runtime_privacy_settings_contract`
- `manual_privacy_review`
- `manual_platform_path_review`
- `upload_transport_runtime_smoke`
- `release_candidate_evidence_gate`

## Manual Checks

| Check | Decision | Status | Required changes |
|---|---|---|---:|
| `privacy_notice_claims` | `needs_more_review` | `draft_todo` | 1 |
| `consent_and_default_off` | `needs_more_review` | `draft_todo` | 1 |
| `prohibited_data_fields` | `needs_more_review` | `draft_todo` | 1 |
| `raw_replay_and_crash_reports` | `needs_more_review` | `draft_todo` | 1 |
| `retention_delete_export` | `needs_more_review` | `draft_todo` | 1 |
| `platform_path_and_local_data_scope` | `needs_more_review` | `draft_todo` | 1 |
| `upload_transport_status` | `needs_more_review` | `draft_todo` | 1 |
| `jurisdiction_and_store_requirements` | `needs_more_review` | `draft_todo` | 1 |
| `release_evidence_limits` | `needs_more_review` | `draft_todo` | 1 |

## Check Details

### privacy_notice_claims

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm privacy notice claims match actual Runtime behavior and do not overstate upload, deletion, export, or platform compliance.

### consent_and_default_off

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm telemetry, raw replay upload, and crash report upload remain default-off and require explicit consent.

### prohibited_data_fields

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm policy and upload contract prohibit personal identity, IP address, host paths, free text, and raw action streams by default.

### raw_replay_and_crash_reports

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm raw replay and crash report handling has separate consent and does not claim implementation before evidence exists.

### retention_delete_export

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm retention, delete, and export statements match policy, local data controls, and release evidence.

### platform_path_and_local_data_scope

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm platform path, save, settings, telemetry, replay, and crash report local data scope has a passed platform path review.

### upload_transport_status

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm upload transport status is accurately represented and does not imply network upload exists while implementation_status is planned.

### jurisdiction_and_store_requirements

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm target jurisdiction/store scope has been reviewed by a qualified human and unresolved requirements are listed.

### release_evidence_limits

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm this review does not claim release readiness, platform approval, accepted content, or Runtime implementation beyond actual evidence.

## Limitations

- This packet organizes manual legal/compliance review evidence only.
- It does not provide legal advice, platform approval, store approval, upload approval, or release approval.
- TODO review fields must be filled by a qualified human before manual legal validation can pass.
- Valid privacy, Runtime, upload, save, privacy-review, and platform-path evidence still does not prove release readiness.
