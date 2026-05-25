# Runtime Simulation Speed Smoke Summary

- Command: `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 60 --demo-input --simulation-speed 8 --playtest-report harness/telemetry/local/runtime_simulation_speed_smoke_001.json --player-skill demo-bot --capture-interval 5 --auto-exit-after-report`
- Report copy: `harness/reports/2026-05-25_runtime_simulation_speed_smoke_001/runtime_simulation_speed_smoke.json`
- Input mode: `demo`
- Simulation speed: `8.0`
- Auto exit after report: `true`
- Capture result: `13` telemetry samples, terminal `victory`, reason `duration_reached`, duration `60.03s`
- Event counts: kills `48`, XP collected `44`, level up `2`, upgrade chosen `2`, run ended `1`
- Wall-clock note: `/usr/bin/time -p` reported `real 31.56` seconds for the full command, including cargo/build startup and Bevy window startup.

## Gate Notes

- Runtime capture can now advance GameCore faster than wall clock when `--simulation-speed` is set.
- The speed multiplier is opt-in and defaults to `1.0`, so normal manual playtest behavior is unchanged.
- The smoke run auto-exited only after the terminal report was successfully written.
- This is still a Runtime visual-client smoke path. High-volume deterministic validation should continue to use headless Harness commands.

## Next Validation

- Keep `--simulation-speed` for scripted Runtime capture only, not for human playtest scoring.
- Use a longer accelerated capture if future visual changes need Boss coverage without a long wall-clock wait.
- True fun, readability, and difficulty notes still require a human playtest capture.
