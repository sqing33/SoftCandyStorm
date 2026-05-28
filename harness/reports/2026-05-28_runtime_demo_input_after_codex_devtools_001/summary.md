# Runtime Performance Capture Validation

- Source: `harness/telemetry/local/runtime_demo_input_after_codex_devtools_001.json`
- Decision: `runtime_performance_capture_valid`
- Input mode: `demo`
- Simulation speed: `8.0`
- Average FPS: `56.99`
- Worst frame FPS: `10.00`
- Slow frames below 30 FPS: `9` / `661`
- Samples: `91`
- Max visible enemies: `5`
- Max visible projectiles: `16`
- Terminal: `victory`
- Duration: `90.03` / `90.00` seconds

## Errors

- None

## Warnings

- None

## Limitations

- This validates one local Runtime playtest capture only; it is not Steam Deck or broad hardware coverage.
- Frame timing comes from Bevy runtime frame deltas and does not replace GPU profiling or memory growth checks.
- Manual playtest readability, fun, death clarity, and content acceptance remain separate human gates.
