# Runtime Native Platform Paths

- Decision: `runtime_native_platform_paths_verified`
- Scope: `crates/game_runtime/src/main.rs`
- Feature: `--native-platform-data-root`

## Implemented

- Added explicit Runtime CLI support for binding default save, settings, telemetry, replay, and crash-report paths to native platform data directories.
- Native directory mapping:
  - macOS: `~/Library/Application Support/Soft Candy Storm`
  - Windows: `%APPDATA%/Soft Candy Storm`, with `~/AppData/Roaming` fallback
  - Linux / Unix: `${XDG_DATA_HOME:-~/.local/share}/soft-candy-storm`
- Added unit coverage for OS-specific path resolution and CLI rebinding of default platform paths.

## Verification

- `cargo fmt --check`: passed
- `cargo test -p game_runtime`: passed, 87 tests

## Limitations

- This is Runtime source and unit-test evidence, not a human platform-path approval.
- Manual platform path review remains pending.
- Cloud save policy, platform privacy text, and release packaging review remain pending.
