# RL Edge-Aux Staged Opening Handoff Trace

- Decision: `edge_aux_staged_opening_handoff_trace_recorded`
- Failure case: `harness/failed_cases/fail_20260527_030_edge_aux_staged_opening_handoff_gap.json`
- Analysis: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_trace_001/trace_analysis.json`
- Policy kind: `staged_sb3_opening_behavior_clone`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/staged.pt`
- Trace mode: failed-only, sample stride `15`

## Reproduction

The failed-only traces reproduce the two `mid_60_to_180` failures from the 180 second handoff probe:

| Map | Seed | Terminal | Level | Kills | Damage | Edge-Risk Samples |
|---|---:|---:|---:|---:|---:|---:|
| `soda-creek` | 62201 | `171.2743s` | 6 | 347 | 120.0703 | 312 / 344 |
| `cracked-star-jar` | 62201 | `157.3380s` | 6 | 266 | 120.2638 | 301 / 316 |

Both episodes preserve the stage01 opening wrapper and fail after the fallback behavior clone takes over. No `policy_adapter` was used.

## Key Frames

| Map | Frame | Time | Action | Health | Position | Edge Risk | Enemy Pressure | Chosen Score |
|---|---|---:|---:|---:|---|---:|---:|---:|
| `soda-creek` | first edge risk | `7.0000s` | 2 | 120.0000 | `(890.9526, 890.9526)` | 0.9581 | 0.0000 | 0.5325 |
| `soda-creek` | last alive edge | `171.0076s` | 5 | 0.9796 | `(-1200.0000, -900.0000)` | 1.0000 | 0.0000 | 0.9358 |
| `soda-creek` | terminal | `171.2743s` | 5 | 0.0000 | `(-1200.0000, -900.0000)` | 1.0000 | 0.2550 | 0.9672 |
| `cracked-star-jar` | first edge risk | `7.5000s` | 2 | 120.0000 | `(954.5918, 950.0000)` | 1.0000 | 0.0000 | 0.4220 |
| `cracked-star-jar` | last alive edge | `157.0046s` | 7 | 2.7498 | `(-1300.0000, -937.2722)` | 1.0000 | 0.5155 | 0.9176 |
| `cracked-star-jar` | terminal | `157.3380s` | 7 | 0.0000 | `(-1300.0000, -937.2722)` | 1.0000 | 0.5005 | 0.9172 |

## Findings

- The failure has not returned to an opening gate issue: both traces survive past 60 seconds and die in the handoff / mid window.
- The fallback behavior clone remains edge-pinned for most sampled frames: `soda-creek` has `90.70%` edge-risk samples and `cracked-star-jar` has `95.25%`.
- Terminal choices are high-confidence blocked-edge actions. On `soda-creek`, action `5` pushes downward at the bottom-left corner; on `cracked-star-jar`, action `7` pushes left while already on the left edge.
- The repair target should now be a trained or explicitly constrained handoff / mid fallback that can move out of edge-pinned states, followed by deterministic 60 second opening and 180 second multi-map checks.

## Limitations

This is diagnostic evidence only. The trace rows are sampled every 15 simulation steps, not full Replay records. The report does not prove a fix, does not support RL policy acceptance, and does not permit stage 03.
