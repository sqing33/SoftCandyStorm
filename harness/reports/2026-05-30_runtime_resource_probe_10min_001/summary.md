# Runtime Resource Probe

- Decision: `runtime_resource_probe_valid`
- Command: `target/debug/game_runtime --content-dir content/base_demo --seed 12345 --map-id frosting-grassland --seconds 600 --demo-input --simulation-speed 30 --playtest-report harness/telemetry/local/runtime_resource_probe_10min_001.json --auto-exit-after-report --capture-interval 30`
- Capture: `harness/telemetry/local/runtime_resource_probe_10min_001.json`
- Profile: `release-local`
- Return code: `0`
- Wall seconds: `47.14`
- Max RSS: `164.14` MiB / `2048.00` MiB
- Performance decision: `runtime_performance_capture_valid`
- Average FPS: `57.91`
- 30 FPS slow frame ratio: `0.0054`
- Samples: `21`
- Terminal: `victory`

## Errors

- None

## Warnings

- None

## Limitations

- This probe measures one local child process via resource.getrusage only.
- ru_maxrss is a peak resident set approximation and is not a heap profile or GPU memory measurement.
- The probe does not replace Steam Deck, broad hardware, GPU profiling, leak analysis, or human readability review.
