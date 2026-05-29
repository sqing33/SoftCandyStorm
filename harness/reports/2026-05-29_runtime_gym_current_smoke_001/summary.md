# Runtime / Gym Current Smoke

- Decision: `runtime_gym_current_smoke_valid`
- Runtime capture: `harness/telemetry/local/runtime_gym_current_smoke_001.json`
- Runtime validation: `harness/reports/2026-05-29_runtime_gym_current_smoke_001/runtime_performance_capture.json`
- Gym status: `ok`
- Gym steps: `61`
- Gym observation length: `145`
- Gym action count: `9`
- Runtime terminal: `victory`
- Runtime duration: `120.031845` / `120.0` seconds
- Runtime average FPS: `58.71495`
- Runtime worst frame FPS: `10.0`
- Runtime samples: `25`
- Runtime max enemies/projectiles: `6` / `7`
- Runtime privacy: local_capture_only `True`, upload `not_implemented`

## Checks

| Check | Status | Summary |
|---|---|---|
| `gym_bridge_smoke` | `pass` | Python Gym wrapper completed the smoke episode through game_harness gym-bridge. |
| `gym_observation_shape` | `pass` | Gym smoke reported a positive observation length. |
| `gym_action_space` | `pass` | Gym smoke reported the expected 9-direction discrete action space. |
| `runtime_capture_command` | `pass` | game_runtime demo-input capture command completed and wrote the capture JSON. |
| `runtime_performance_capture` | `pass` | Runtime capture passed local performance, sample, terminal, and entity-count validation. |
| `runtime_privacy_defaults` | `pass` | Runtime capture kept local-only privacy defaults with no upload transport enabled. |

## Commands

| Command | Return | Expected |
|---|---:|---:|
| `/Library/Developer/CommandLineTools/usr/bin/python3 python/gym_env/smoke_test.py` | 0 | 0 |
| `cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 120.0 --demo-input --simulation-speed 30.0 --playtest-report /Users/chongqing/Codes/软糖风暴/harness/telemetry/local/runtime_gym_current_smoke_001.json --player-skill demo-bot --capture-interval 5.0 --auto-exit-after-report` | 0 | 0 |

## Errors

- None

## Limitations

- This smoke is one local technical run; it is not a human playtest.
- Runtime frame metrics come from Bevy frame deltas and do not replace GPU profiling or memory growth checks.
- The Gym bridge smoke is a short wrapper/shape check, not RL policy acceptance or high-pressure training evidence.
- Manual readability, fun, device input review, platform privacy review, and release gates remain separate blockers.
