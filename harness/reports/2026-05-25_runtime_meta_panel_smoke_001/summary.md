# Runtime Meta Panel Smoke Summary

- Command: `cargo run -q -p game_runtime -- --seconds 1 --demo-input --simulation-speed 20 --playtest-report harness/reports/2026-05-25_runtime_meta_panel_smoke_001/runtime_playtest.json --auto-exit-after-report --capture-interval 0.5`
- Result: Runtime started, advanced a 1 second demo-input run, reached terminal, wrote `runtime_playtest.json`, and exited automatically.
- Final terminal: `victory` with reason `duration_reached` at `1.0000004` seconds.
- Samples captured: `3`
- Event counts: `enemy_spawned=1`, `weapon_fired=2`, `run_ended=1`

## Gate Notes

- This smoke checks that the Runtime meta panel integration does not break startup, terminal handling, or capture writing.
- The right-side panel text is covered by the `meta_panel_highlights_last_settlement` unit test.
- This smoke is not a human visual acceptance pass and does not replace the 9-run manual playtest matrix.
