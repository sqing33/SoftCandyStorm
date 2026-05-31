# RL Lane Repair Action Plan

- Decision: `rl_lane_repair_action_plan_ready`
- Lane: `retention63405`
- Lane status: `failed`
- Classification: `opening_mid_boundary_path_retention`

## Diagnostic Summary

- Episode delta: `-75.8496` seconds
- First divergent action: `13.0001`s, `3` -> `7`
- First high pressure: parent `100.9988`s, candidate `45.9996`s
- Negative route_recovery: `248` / `356` (`0.6966`)
- Opening + mid hotspot ratio: `0.8992`
- Boundary-edge hotspot ratio: `0.9516`

## Hotspot Counts

| Group | Count |
|---|---:|
| `opening_lt_60` | 67 |
| `mid_60_to_180` | 156 |
| `late_180_to_300` | 25 |
| `boundary_edge` | 236 |
| `hazard_pressure` | 33 |
| `low_health` | 2 |

## Action Plan

### Objective Scope
- opening_lt_60 boundary escape / route retention
- mid_60_to_180 boundary/path retention

### Candidate Repair Shapes
- lane-specific reward/profile or adapter focused on boundary_edge route recovery
- narrow state-conditioned branch triggered by boundary pressure and bad route_recovery
- small-step continuation only after predefining all hard preflights

### Required Gates
- target seed 63405 180s retention preflight must pass
- 60s/caramel-workshop window target preflight must pass
- 60/180/300s high-pressure parent no-regression must pass
- 10 seed caramel-workshop follow-up must not hide seed-local tradeoffs
- failure-case review must stay attached if any gate fails

### Disallowed Next Steps
- pure late low-health continuation
- shared PPO continuation that also tries to solve target63407
- relaxing short60 or parent-preservation gates to make the lane pass

- Acceptance boundary: This plan is repair routing only; it is not RL acceptance, stage 03 approval, or policy-candidate approval.

## Limitations

- This plan reads existing diagnostics only; it does not rerun simulation or train a policy.
- Sampled traces can miss unsampled frames and do not replace Replay or GameCore snapshots.
- Any follow-up checkpoint still requires target preflight, fixed-window no-regression, failure-case review, and RL acceptance gates.
