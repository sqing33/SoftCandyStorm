# Runtime Playtest Capture Smoke Summary

- Command: `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 60 --playtest-report harness/telemetry/local/runtime_manual_playtest_001.json --player-skill agent-smoke --capture-interval 1`
- Report copy: `harness/reports/2026-05-25_runtime_playtest_capture_smoke_001/runtime_playtest_capture.json`
- Capture result: `61` telemetry samples, terminal `victory`, duration `60.03s`
- Final metrics: level `1`, kills `46`, damage taken `0.0`, max enemies `3`, max projectiles `3`
- Event counts: weapon fired `97`, enemy hit `93`, enemy killed `46`, XP dropped `46`, run ended `1`

## Gate Notes

- Runtime capture JSON was written successfully and includes run config, event counts, per-second samples, final metrics, and manual review fields.
- The smoke run validates the capture pipeline and passive runtime loop, not a true human fun judgement.
- Keyboard-driven player movement, XP pickup rhythm, upgrade selection, Boss readability, and death reason clarity remain unverified in this run because the app window could not be reliably focused for input injection.

## Next Validation

- Run a real local manual playtest with `--playtest-report` enabled.
- Fill `manual_review` fields after the run.
- If UI automation remains necessary, add a dedicated deterministic runtime demo input mode instead of treating no-input capture as manual feedback.
