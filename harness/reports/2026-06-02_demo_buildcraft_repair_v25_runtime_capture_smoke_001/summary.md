# Runtime Performance Capture Validation

- Source: `harness/reports/2026-06-02_demo_buildcraft_repair_v25_runtime_capture_smoke_001/runtime_capture.json`
- Profile: `smoke`
- Decision: `runtime_performance_capture_valid`
- Input mode: `demo`
- Simulation speed: `30.0`
- Average FPS: `58.73`
- Worst frame FPS: `10.00`
- Slow frames below 30 FPS: `3` / `391`
- Samples: `46`
- Max visible enemies: `5`
- Max visible projectiles: `6`
- Terminal: `victory`
- Duration: `90.03` / `90.00` seconds

## Errors

- None

## Warnings

- None

## Limitations

- This validates one local Runtime playtest capture only; it is not Steam Deck or broad hardware coverage.
- The release-local profile is stricter than smoke, but still remains a single-machine automated gate.
- Frame timing comes from Bevy runtime frame deltas and does not replace GPU profiling or memory growth checks.
- Manual playtest readability, fun, death clarity, and content acceptance remain separate human gates.
