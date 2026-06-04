# v51 Runtime Smoke

- Candidate id: `2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Content hash: `fnv1a64:50bd536bd0669e2b`
- Content dir: `harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Decision: `runtime_smoke_blocked_gpu_unavailable_headless_content_valid`

## Runtime Quick Play

- Command: `python3 harness/playtest/play_current_candidate.py --seconds 20 --capture-interval 2`
- Runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack --character-id jar-keeper --map-id frosting-grassland --seed 55101 --seconds 20 --player-skill quickplay --playtest-report harness/telemetry/local/v51_quick_play_default.json --capture-interval 2`
- Result: failed before report capture
- Exit code: `101`
- Build: compiled successfully
- Error: `Unable to find a GPU! Make sure you have installed required drivers!`

## Headless Evidence

- `game_harness validate-content`: `ok`, `91` objects, no warnings
- `game_harness simulate`: `20s`, seed `55101`, bot `kite`, terminal `victory`, reason `duration_reached`
- Sim metrics: `13` kills, level `1`, XP collected `22.0`, damage taken `0.0`, max enemies `5`

## Failure Case

- `harness/failed_cases/fail_20260604_004_v51_runtime_gpu_unavailable.json`

## Conclusion

The current environment blocks Bevy/WGPU GUI startup, but the v51 generated content pack loads and simulates in headless GameCore. This is a Runtime environment blocker, not evidence that the content pack is broken.

## Next Actions

- Rerun the quick-play Runtime command from a GPU-capable desktop session before using it as human playtest evidence.
- Keep using headless Harness validation and simulation for generated-content checks in this environment.
- Do not promote v51 into `content/base_demo`, `playtest_candidates`, `accepted_content`, or Runtime official content based on this smoke.

## Limitations

- This smoke does not judge fun, clarity, input feel, rendering, audio, or human playtest readiness.
- Headless checks are content-loading and short simulation evidence only.
- v51 remains a generated candidate.
