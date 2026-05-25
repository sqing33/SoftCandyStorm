# Runtime Demo Input Capture Summary

- Command: `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 90 --demo-input --playtest-report harness/telemetry/local/runtime_demo_input_001.json --player-skill demo-bot --capture-interval 1`
- Report copy: `harness/reports/2026-05-25_runtime_demo_input_001/runtime_demo_input_capture.json`
- Input mode: `demo`
- Capture result: `91` telemetry samples, terminal `victory`, duration `90.03s`
- Final metrics: level `4`, kills `69`, damage taken `0.0`, max enemies `5`, max projectiles `6`
- Event counts: XP collected `69`, level up `3`, upgrade offered `3`, upgrade chosen `3`, run ended `1`
- Upgrade choices: `candy-crystal-lens`, `big-candy-jar`, `bubble-shoes`

## Gate Notes

- Demo input proves Runtime can drive deterministic movement and upgrade selection without relying on window focus.
- This capture covers movement, projectile firing, enemy hit/kill feedback, XP pickup, level-up offer, upgrade choice, final metrics, and report writing.
- Boss readability and damage/death clarity remain uncovered because the run ended before the 210s Boss event and took no player damage.

## Next Validation

- Run a longer demo capture past `210s` to cover Boss spawn visibility.
- Tune demo movement or content pressure so at least one capture includes player damage without collapsing the run.
- Still run a true human playtest before treating Phase 2 manual fun/clarity requirements as satisfied.
