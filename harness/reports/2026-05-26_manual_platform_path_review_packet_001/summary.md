# Manual Platform Path Review Packet

- Review template: `harness/save_contract/manual_platform_path_review_template.json`
- Gate decision: `needs_more_review`
- Summary status: `draft_todo`
- Path policy: `harness/save_contract/platform_save_path_policy_v0.json`
- Path policy validation report: `harness/reports/2026-05-26_save_path_policy_v0_001/summary.md`
- Save contracts: 2
- Storage roots: 5
- Checks: 7
- Draft TODO checks: 7

## Policy Summary

- Policy id: `platform-save-path-v0`
- Scope: `local-save-and-runtime-data`
- Status: `contract-only`

## Storage Roots

| Root | Purpose | Logical path | Delete | Export | Cloud sync |
|---|---|---|---|---|---|
| `save_files` | `player_save_state` | `platform_user_data/soft-candy-storm/saves` | `True` | `True` | `False` |
| `runtime_settings` | `runtime_privacy_settings` | `platform_user_data/soft-candy-storm/settings` | `True` | `True` | `False` |
| `local_telemetry` | `local_telemetry_cache` | `platform_user_data/soft-candy-storm/telemetry` | `True` | `True` | `False` |
| `local_replay` | `local_replay_cache` | `platform_user_data/soft-candy-storm/replay` | `True` | `True` | `False` |
| `crash_reports` | `local_crash_report_cache` | `platform_user_data/soft-candy-storm/crash-reports` | `True` | `True` | `False` |

## Path Rules

- `cloud_sync_requires_manual_review`: `True`
- `delete_requires_explicit_user_action`: `True`
- `delete_scope_must_be_configured_roots`: `True`
- `export_format_json`: `True`
- `local_only_by_default`: `True`
- `migration_must_keep_original_until_success`: `True`
- `no_absolute_paths_in_save`: `True`
- `no_personal_identity_in_paths`: `True`
- `platform_paths_must_be_reviewed_before_release`: `True`
- `player_visible_delete_export`: `True`

## Prohibited Path Fragments

- `/Users/`
- `C:\`
- `~/`
- `email`
- `ip_address`
- `player_name`
- `real_name`
- `absolute_path`
- `free_text_input`

## Save Contracts

| Contract | Schema | Path |
|---|---|---|
| `save-state-v0` | `1` | `harness/save_contract/save_state_v0_template.json` |
| `save-state-v1` | `2` | `harness/save_contract/save_state_v1_template.json` |

## Release Requirements

- `manual_privacy_review`
- `platform_path_review`
- `delete_export_controls`
- `save_migration_fixtures`
- `release_candidate_evidence_gate`

## Policy Blockers

- Runtime does not resolve platform-native save paths
- Platform save path review is not complete
- Cloud save policy is not defined

## Manual Checks

| Check | Decision | Status | Required changes |
|---|---|---|---:|
| `logical_roots` | `needs_more_review` | `draft_todo` | 1 |
| `no_host_absolute_paths` | `needs_more_review` | `draft_todo` | 1 |
| `delete_scope` | `needs_more_review` | `draft_todo` | 1 |
| `export_scope` | `needs_more_review` | `draft_todo` | 1 |
| `migration_original_retention` | `needs_more_review` | `draft_todo` | 1 |
| `cloud_sync_policy` | `needs_more_review` | `draft_todo` | 1 |
| `runtime_evidence_limits` | `needs_more_review` | `draft_todo` | 1 |

## Check Details

### logical_roots

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm save, settings, telemetry, replay, and crash report logical roots are platform-safe.

### no_host_absolute_paths

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm saves and exported records do not persist /Users, drive letters, home paths, or other host-specific absolute paths.

### delete_scope

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm delete operations can only affect configured local data roots and require explicit user action.

### export_scope

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm export operations produce JSON from configured local data roots without personal host paths.

### migration_original_retention

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm migration keeps the original save until target write and validation succeed.

### cloud_sync_policy

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm cloud sync remains disabled or has a separate reviewed policy before release.

### runtime_evidence_limits

- Decision: `needs_more_review`
- Status: `draft_todo`
- Notes: TODO: confirm this review does not claim Runtime platform path implementation, platform approval, legal approval, cloud save support, or release readiness.

## Limitations

- This packet organizes manual platform path review evidence only.
- It does not provide legal advice, platform approval, cloud save approval, Runtime implementation proof, or release approval.
- TODO review fields must be filled by a qualified human before manual platform path validation can pass.
- A valid path policy does not prove executable Runtime platform-native path behavior.
