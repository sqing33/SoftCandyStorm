# RL Failure Lane Repair Preflight

- Decision: `rl_failure_lane_repair_preflight_ready`
- Source trace summary: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_lane_trace_summary.json`
- Map: `caramel-workshop`
- Gate conclusion: `repair`

## Preflight Lanes

| Lane | Classification | Repair Shape | Dominant Action | Negative Samples | Required Preflights |
|---|---|---|---|---:|---|
| `opening_repair` | `opening_boundary_action_lock` | narrow state-conditioned opening branch or target-seed preflight | `5` | 51 (62.20%) | opening_seed63402_target_preflight, short60_caramel_window_preflight, high_pressure_parent_no_regression |
| `late_terminal_survival_conversion` | `terminal_conversion_with_opening_mid_route_debt` | path-retention-preserving terminal conversion | `5` | 2599 (74.71%) | caramel_300s_10seed_followup, short60_caramel_window_preflight, high_pressure_parent_no_regression |

## Blocked Patterns

### `opening_repair`
- shared PPO continuation that also targets late_terminal_survival_conversion
- broad 0-60s branch without online action-distribution regression review
- treating route hotspot evidence as policy acceptance

### `late_terminal_survival_conversion`
- pure 180s+ low-health-only continuation
- terminal branch that ignores 60-180s path retention debt
- using unfiltered continuous-seed trace hotspots as late-only evidence

## Blocked Until

- opening_repair and late_terminal_survival_conversion are validated as separate lanes
- short60_caramel_window_preflight passes
- high_pressure_parent_no_regression passes for 60/180/300 seconds
- 10 seed caramel follow-up does not regress baseline evidence

## Limitations

- This report creates a preflight contract only; it does not run simulation or train a policy.
- Trace diagnostics are sampled evidence and must not be treated as Replay regression.
- A ready decision is repair routing evidence, not policy acceptance or RL test Bot approval.
