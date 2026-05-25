# Runtime Boss Capture Summary

- Command: `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 240 --demo-input --playtest-report harness/telemetry/local/runtime_boss_capture_001.json --player-skill demo-bot --capture-interval 2`
- Report copy: `harness/reports/2026-05-25_runtime_boss_capture_001/runtime_boss_capture.json`
- Input mode: `demo`
- Capture result: `121` telemetry samples, terminal `victory`, reason `duration_reached`, duration `240.02s`
- Final metrics: level `10`, kills `368`, damage taken `18.90`, max enemies `18`, max projectiles `6`
- Event counts: Boss spawned `1`, player damaged `37`, XP collected `363`, level up `9`, upgrade offered `9`, upgrade chosen `9`, run ended `1`
- Upgrade choices: `bubble-shoes`, `rainbow-candy-shot-level-2`, `star-spoon`, `candy-crystal-lens`, `rainbow-candy-shot-level-3`, `bubble-shoes`, `candy-crystal-lens`, `candy-crystal-lens`, `star-spoon`

## Gate Notes

- Demo input now proves Runtime capture can cover deterministic movement, XP pickup, upgrade choice, Boss spawn feedback, player damage feedback, final metrics, terminal state, and report writing.
- This is still an automated technical capture, not a human playability judgment. Boss readability, hit readability, difficulty feel, and death-cause clarity still need manual notes.
- The Bevy Runtime did not automatically close after writing the terminal report; the process was stopped after verifying that `final_metrics.terminal` and `run_ended` were present in the copied report.
- Wall-clock runtime was much longer than configured game time in the desktop environment, so batch-style Runtime capture would benefit from a future accelerated or auto-exit mode.

## Next Validation

- Run a true human playtest with the same capture path and fill the manual review fields.
- Add an optional Runtime auto-exit flag after terminal report write, so future capture runs can be scripted without manual process termination.
- Consider a Runtime fast-forward or offscreen capture mode only if repeated visual capture becomes part of the regular gate.
