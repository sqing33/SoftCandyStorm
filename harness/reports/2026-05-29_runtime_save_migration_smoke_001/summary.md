# Runtime Save Migration Smoke

- Decision: `runtime_save_migration_smoke_valid`
- Work dir: `/private/tmp/soft-candy-runtime-save-migration-smoke-001`
- Template: `harness/save_contract/save_state_v0_template.json`

## Checks

| Check | Status | Summary |
|---|---|---|
| `runtime_command_migrates_v0` | `pass` | Runtime prelaunch export command completed and printed the export path. |
| `save_file_rewritten_to_v1` | `pass` | Original save file was rewritten from save-state-v0 to save-state-v1. |
| `export_file_written_as_v1` | `pass` | Exported save file uses save-state-v1. |
| `migration_history_completed` | `pass` | Migrated and exported saves record one completed save-state-v0-to-v1 migration entry. |
| `meta_progress_preserved` | `pass` | Resources, unlocks, chapters, completed runs, and best survival are preserved. |
| `privacy_and_data_controls_preserved` | `pass` | Privacy defaults and local-only data controls remain preserved after migration. |
| `base_ui_state_initialized` | `pass` | save-state-v1 base_ui_state is initialized for Runtime meta panel persistence. |

## Commands

| Command | Return | Expected |
|---|---:|---:|
| `cargo run -p game_runtime -- --save-file /private/tmp/soft-candy-runtime-save-migration-smoke-001/profile_v0.json --export-save /private/tmp/soft-candy-runtime-save-migration-smoke-001/profile_export_v1.json` | 0 | 0 |

## Errors

- None

## Limitations

- This smoke executes Runtime prelaunch CLI actions only; it does not open the Bevy window.
- It validates one seeded save-state-v0 migration sample, not every historical save.
- It does not replace manual platform path review, cloud save policy, or release candidate approval.
