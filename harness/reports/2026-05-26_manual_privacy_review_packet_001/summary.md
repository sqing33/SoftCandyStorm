# Manual Privacy Review Packet

- Review template: `harness/telemetry_privacy/manual_privacy_review_template.json`
- Gate decision: `needs_more_review`
- Summary status: `draft_todo`
- Policy: `harness/telemetry_privacy/telemetry_privacy_policy_template.json`
- Runtime privacy contract: `harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json`
- Save contract: `harness/save_contract/save_state_v0_template.json`
- Policy validation report: `harness/reports/<policy-validation>/summary.md`
- Runtime contract validation report: `harness/reports/<runtime-contract-validation>/summary.md`
- Checks: 8
- Draft TODO checks: 8

## Policy Summary

- Policy id: `local-first-telemetry-privacy-v001`
- Scope: `development-local`
- Upload enabled: `False`
- Upload default enabled: `False`
- Upload requires consent: `True`
- Raw replay default enabled: `False`
- Raw replay requires consent: `True`
- Retention days: `30`

## Prohibited Fields

- `personal_identity`
- `email`
- `ip_address`
- `file_path`
- `free_text_input`
- `raw_replay_action_stream`

## Allowed Event Fields

- `timestamp`
- `run_id`
- `session_id`
- `game_version`
- `content_hash`
- `map_id`
- `character_id`
- `difficulty`
- `elapsed_seconds`
- `event_type`
- `event_counts`
- `final_metrics`

## Runtime UI Controls

| Control | Setting | Default | Consent |
|---|---|---|---|
| `telemetry_upload_toggle` | `telemetry_upload_enabled` | `False` | `True` |
| `raw_replay_upload_toggle` | `raw_replay_upload_enabled` | `False` | `True` |
| `crash_report_upload_toggle` | `crash_report_upload_enabled` | `False` | `True` |

## Data Action Controls

| Control | Action | Visible |
|---|---|---|
| `delete_local_telemetry` | `delete_local_data` | `True` |
| `export_local_telemetry` | `export_local_data` | `True` |
| `open_privacy_notice` | `open_privacy_notice` | `True` |

## Privacy Notice Topics

- `purposes`
- `anonymous_session`
- `default_off`
- `delete_export`
- `raw_replay_separate_consent`
- `prohibited_fields`
- `retention_days`

## Privacy Notice Text

遥测和 Replay 默认只保存在本机。上传匿名遥测、原始 Replay 输入或崩溃报告前，游戏必须先征得你的明确同意；你可以随时关闭上传、删除本地数据或导出 JSON 副本。

## Manual Checks

| Check | Decision | Status | Required changes |
|---|---|---|---:|
| `default_off` | `needs_more_review` | `draft_todo` | 1 |
| `explicit_consent` | `needs_more_review` | `draft_todo` | 1 |
| `raw_replay_separate_consent` | `needs_more_review` | `draft_todo` | 1 |
| `prohibited_fields` | `needs_more_review` | `draft_todo` | 1 |
| `delete_export_controls` | `needs_more_review` | `draft_todo` | 1 |
| `privacy_notice_text` | `needs_more_review` | `draft_todo` | 1 |
| `retention_and_storage` | `needs_more_review` | `draft_todo` | 1 |
| `runtime_evidence_limits` | `needs_more_review` | `draft_todo` | 1 |

## Check Details

### default_off

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm telemetry, raw replay upload, and crash report upload default to off.

### explicit_consent

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm each upload category requires explicit, separate consent.

### raw_replay_separate_consent

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm raw replay input upload is separate from aggregate telemetry.

### prohibited_fields

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm personal identity, email, IP address, file paths, free text, and raw action streams are prohibited by default.

### delete_export_controls

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm delete and export local data controls are visible and understandable.

### privacy_notice_text

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm the zh-CN privacy notice explains purposes, local-first defaults, retention, prohibited fields, and controls.

### retention_and_storage

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm retention days and local storage paths are documented and bounded.

### runtime_evidence_limits

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm the review does not claim upload transport, platform privacy compliance, or release readiness before evidence exists.

## Limitations

- This packet organizes manual privacy review evidence only.
- It does not provide legal advice, platform approval, upload transport proof, or release approval.
- TODO review fields must be filled by a qualified human before manual privacy validation can pass.
- Valid policy and Runtime setting contracts do not prove executable Runtime behavior or network upload behavior.
