# Runtime Demo Capture After Restart

- Command: `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 240 --demo-input --simulation-speed 8 --auto-exit-after-report --playtest-report harness/telemetry/local/runtime_demo_capture_after_restart_001.json --player-skill demo-bot --capture-interval 2`
- Report copy: `harness/reports/2026-05-26_runtime_demo_capture_after_restart_001/runtime_demo_capture_after_restart.json`
- Input mode: `demo`
- Simulation speed: `8.0`
- Auto exit after report: `true`
- Capture result: `121` telemetry samples, terminal `victory`, reason `duration_reached`, duration `240.02s`
- Final metrics: level `10`, kills `403`, damage taken `73.33`, max enemies `11`, max projectiles `21`
- Event counts: Boss spawned `1`, Boss phase changed `1`, Boss abilities `5`, player damaged `110`, XP collected `336`, level up `9`, upgrade offered `9`, upgrade chosen `9`, run ended `1`
- Upgrade choices: `rainbow-candy-shot-level-2`, `rainbow-candy-shot-level-3`, `rainbow-candy-shot-level-4`, `rainbow-candy-shot-level-5`, `soda-bubble-pop`, `soda-bubble-pop-level-2`, `soda-bubble-pop-level-3`, `soda-bubble-pop-level-4`, `soda-bubble-pop-level-5`

## Gate Notes

- This current-session capture proves the Bevy Runtime can launch after the local binary recovery, run deterministic demo input, write telemetry samples, record upgrades, cover Boss spawn / phase / ability events, record player damage feedback, write final metrics, and exit automatically after the terminal report.
- This is automated technical evidence only. It does not fill the 9-run human playtest matrix, human readability ratings, asset acceptance, story / codex acceptance, or Release Candidate manual gates.

## Next Validation

- Run true human playtest sessions with the same capture path and fill the manual review fields.
- Use this capture as the current Runtime smoke evidence when refreshing roadmap and docs coverage ledgers.
