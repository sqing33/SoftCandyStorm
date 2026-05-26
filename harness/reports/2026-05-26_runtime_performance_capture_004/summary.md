# Runtime Performance Capture Validation

- Source: `harness/telemetry/local/runtime_performance_smoke_2026-05-26_004.json`
- Decision: `runtime_performance_capture_valid`
- Input mode: `demo`
- Simulation speed: `1.0`
- Average FPS: `48.31`
- Worst frame FPS: `10.00`
- Slow frames below 30 FPS: `15` / `395`
- Samples: `11`
- Max visible enemies: `2`
- Max visible projectiles: `3`
- Terminal: `victory`
- Duration: `10.00` / `10.00` seconds

## Errors

- None

## Warnings

- None

## Limitations

- This validates one local Runtime playtest capture only; it is not Steam Deck or broad hardware coverage.
- Frame timing comes from Bevy runtime frame deltas and does not replace GPU profiling or memory growth checks.
- Manual playtest readability, fun, death clarity, and content acceptance remain separate human gates.
