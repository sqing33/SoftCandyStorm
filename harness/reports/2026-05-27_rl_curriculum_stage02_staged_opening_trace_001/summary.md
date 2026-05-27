# RL Curriculum Stage 02 Staged Opening Trace

- Decision: `stage02_staged_opening_trace_recorded`
- Failure case: `harness/failed_cases/fail_20260527_027_stage02_staged_opening_mid_regression.json`
- Evaluation: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_trace_001/evaluation.json`
- Trace: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_trace_001/traces/soda-creek_seed62201_trace.json`
- Analysis: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_trace_001/trace_analysis.json`

## Reproduction

- Map: `soda-creek`
- Seed: `62201`
- Opening model: `stage01_corner_risk_delta_smoke.zip`
- Fallback model: `stage02_opening_edge_delta.zip`
- Opening duration: `60s`
- Trace mode: failed-only, sample stride `15`

The episode reproduces the staged policy failure: `player_health_depleted` at `115.5319s`, level `4`, kills `168`, damage taken `120.1636`.

## Key Frames

| Time | Action | Health | Position | Boundary Min | Enemy Pressure | Low Health | Nearest Hitbox | Chosen Score |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| `59.9994s` | `7` | 92.4698 | `(-1200.0, -900.0)` | 0.0 | 0.0 | 0.0 | 408.7298 | 0.8927 |
| `74.9992s` | `7` | 59.7596 | `(-1200.0, -900.0)` | 0.0 | 0.8671 | 0.0 | 0.0 | 0.8590 |
| `89.9990s` | `7` | 24.8195 | `(-1200.0, -895.7574)` | 0.0 | 0.0 | 0.4091 | 446.1207 | 0.6697 |
| `115.5319s` | `7` | 0.0 | `(-1200.0, -895.7574)` | 0.0 | 0.5045 | 1.0 | 0.0 | 0.8487 |

## Findings

- At the 60-second handoff the opening model has survived, but the player is already pinned at the left-bottom boundary.
- From `60s` to `75s`, every sampled action is `7`; at the left boundary this keeps pushing into the wall instead of recovering toward open space.
- The first post-handoff sampled damage appears at `68.9993s`, and by `74.9992s` a `bouncy-gummy` is in direct contact.
- The `75s-90s` bucket reaches `enemy_pressure_risk = 1.0`; low health starts at `76.9992s`, but sampled actions only alternate between `4` and `7`.
- The final collapse returns to persistent action `7`, with the player still boundary-pinned when the terminal contact lands.

## Conclusion

The staged opening wrapper fixes the opening gate but hands stage 02 a bad mid-window state: alive, corner-pinned, and still highly confident in action `7`. The next repair target should be handoff recovery from an edge-pinned state, with explicit checks that the policy can move back into open space before enemy pressure attaches.

This trace is diagnostic evidence only. It is not a Replay, not a fix, and not RL policy acceptance.
