# Runtime Performance Capture Validation

- Source: `harness/telemetry/local/runtime_demo_input_10min_001.json`
- Decision: `runtime_performance_capture_valid`
- Input mode: `demo`
- Simulation speed: `30.0`
- Average FPS: `58.65`
- Worst frame FPS: `10.00`
- Slow frames below 30 FPS: `6` / `2598`
- Samples: `21`
- Max visible enemies: `8`
- Max visible projectiles: `48`
- Terminal: `victory`
- Duration: `600.01` / `600.00` seconds

## Errors

- None

## Warnings

- None

## Limitations

- This validates one local Runtime playtest capture only; it is not Steam Deck or broad hardware coverage.
- Frame timing comes from Bevy runtime frame deltas and does not replace GPU profiling or memory growth checks.
- Manual playtest readability, fun, death clarity, and content acceptance remain separate human gates.
