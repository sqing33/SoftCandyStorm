# Runtime Local Data Controls Smoke

- Decision: `runtime_local_data_controls_smoke_valid`
- Work dir: `harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work`
- Platform data root: `harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm`

## Checks

| Check | Status | Summary |
|---|---|---|
| `privacy_notice_defaults_local` | `pass` | Privacy notice prints local-only defaults, explicit opt-in language, and no upload transport. |
| `save_export_created_v1` | `pass` | Save export creates a save-state-v1 profile with local-only default data controls. |
| `save_delete_requires_explicit_save_file` | `pass` | Save deletion through platform data root is rejected unless --save-file is explicit. |
| `save_delete_removes_explicit_file` | `pass` | Explicit --save-file deletion removes only the selected profile file. |
| `local_data_export_includes_configured_platform_dirs` | `pass` | Local data export includes telemetry, replay, and crash-report files from the platform data root. |
| `local_data_delete_requires_explicit_dirs` | `pass` | Local data deletion is rejected when only --platform-data-root provided implicit directories. |
| `local_data_delete_removes_explicit_dirs` | `pass` | Local data deletion clears files under every explicit --local-data-dir while preserving the root dirs. |

## Commands

| Command | Return | Expected |
|---|---:|---:|
| `cargo run -p game_runtime -- --platform-data-root harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm --print-privacy-notice` | 0 | 0 |
| `cargo run -p game_runtime -- --platform-data-root harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm --export-save harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/artifacts/profile_export.json` | 0 | 0 |
| `cargo run -p game_runtime -- --platform-data-root harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm --delete-save` | 2 | 2 |
| `cargo run -p game_runtime -- --save-file harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm/saves/profile.json --delete-save` | 0 | 0 |
| `cargo run -p game_runtime -- --platform-data-root harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm --export-local-data harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/artifacts/local_data_export.json` | 0 | 0 |
| `cargo run -p game_runtime -- --platform-data-root harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm --delete-local-data` | 2 | 2 |
| `cargo run -p game_runtime -- --local-data-dir harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm/telemetry --local-data-dir harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm/replay --local-data-dir harness/reports/2026-05-29_runtime_local_data_controls_smoke_001/work/platform_user_data/soft-candy-storm/crash-reports --delete-local-data` | 0 | 0 |

## Errors

- None

## Limitations

- This smoke executes Runtime prelaunch CLI actions only; it does not open the Bevy window.
- It validates local JSON export/delete behavior, not native OS platform data resolution.
- It does not replace manual privacy review, manual platform path review, legal review, or release candidate approval.
- Upload transport remains intentionally not implemented for this prototype.
