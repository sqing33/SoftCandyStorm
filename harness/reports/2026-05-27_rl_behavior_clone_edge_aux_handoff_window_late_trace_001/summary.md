# RL Edge-Aux Handoff-Window Late Trace

- Decision: `edge_aux_handoff_window_late_trace_recorded`
- Failure case: `harness/failed_cases/fail_20260527_031_edge_aux_handoff_window_late_gap.json`
- Source comparison: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_late_trace_001/comparison_300s_3seed_trace.json`
- Analysis: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_late_trace_001/trace_analysis.json`
- Trace mode: failed-only, sample stride `30`

## Result

The trace run reproduces the 300 second late-window regression from the handoff-window staged clone. It records 8 failed policy episodes:

| Map | Traces | Average Terminal Time | Terminal Edge-Pinned | Terminal Hazard Pressure | Terminal Boss Pressure |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 3 | 237.2439 | 3 | 1 | 2 |
| `caramel-workshop` | 3 | 220.2403 | 2 | 3 | 2 |
| `cracked-star-jar` | 2 | 207.0152 | 2 | 1 | 1 |

Across all terminal frames, 7 / 8 are edge-pinned, 5 / 8 include hazard pressure, 5 / 8 include boss pressure, and 5 / 8 end with direct enemy contact.

## Interpretation

The late-window failure is no longer a pure copy of the 60-180 second handoff bug. Late edge recovery is still a major issue, but the terminal frames also show mixed hazard and boss pressure, especially on `caramel-workshop` and `cracked-star-jar`.

The next repair should target 180-300 second recovery as a combined objective: leave bad edges, avoid hazard fields, and survive boss / enemy pressure while low health is rising. This remains diagnostic evidence only and does not permit stage 03 or RL policy acceptance.

## Trace Files

- `traces/soda-creek_seed62300_trace.json`
- `traces/soda-creek_seed62301_trace.json`
- `traces/soda-creek_seed62302_trace.json`
- `traces/caramel-workshop_seed62300_trace.json`
- `traces/caramel-workshop_seed62301_trace.json`
- `traces/caramel-workshop_seed62302_trace.json`
- `traces/cracked-star-jar_seed62300_trace.json`
- `traces/cracked-star-jar_seed62301_trace.json`
