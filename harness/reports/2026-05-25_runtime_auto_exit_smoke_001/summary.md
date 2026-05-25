# Runtime Auto Exit Smoke Summary

- Command: `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 5 --demo-input --playtest-report harness/telemetry/local/runtime_auto_exit_smoke_001.json --player-skill demo-bot --capture-interval 1 --auto-exit-after-report`
- Report copy: `harness/reports/2026-05-25_runtime_auto_exit_smoke_001/runtime_auto_exit_smoke.json`
- Input mode: `demo`
- Auto exit after report: `true`
- Capture result: `6` telemetry samples, terminal `victory`, reason `duration_reached`, duration `5.03s`
- Event counts: kills `3`, XP collected `2`, run ended `1`

## Gate Notes

- Runtime exits automatically after the terminal capture report is written when `--auto-exit-after-report` is enabled.
- The flag is opt-in, so normal manual playtest windows remain open after terminal state unless the user closes them.
- This smoke run only validates report write and process exit behavior; it does not replace the longer Boss capture or human playtest.
