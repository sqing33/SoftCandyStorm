# Runtime Performance Capture Validation

- Source: `harness/telemetry/local/v61_quick_play_default.json`
- Profile: `smoke`
- Decision: `runtime_performance_capture_valid`
- Input mode: `keyboard`
- Simulation speed: `1.0`
- Average FPS: `58.80`
- Worst frame FPS: `10.00`
- Slow frames below 30 FPS: `3` / `1169`
- Samples: `11`
- Max visible enemies: `2`
- Max visible projectiles: `3`
- Terminal: `victory`
- Duration: `20.00` / `20.00` seconds

## Errors

- None

## Warnings

- None

## Limitations

- This validates one local Runtime playtest capture only; it is not Steam Deck or broad hardware coverage.
- The release-local profile is stricter than smoke, but still remains a single-machine automated gate.
- Frame timing comes from Bevy runtime frame deltas and does not replace GPU profiling or memory growth checks.
- Manual playtest readability, fun, death clarity, and content acceptance remain separate human gates.
