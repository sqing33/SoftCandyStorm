# Policy Window Target Preflight

- Decision: `policy_window_target_preflight_passed`
- Comparison: `harness/reports/2026-05-31_rl_failure_lane_opening_repair_branch_preflight_001/opening_branch_high_pressure_60s_window0_60.json`
- Target: `short60_caramel_window0_60` / `caramel-workshop`

## Result

| Metric | Value |
|---|---:|
| Win rate | `0.6667` |
| Average survival seconds | `55.9217` |
| Normalized action entropy | `0.4817` |
| Dominant action ratio | `0.6243` |

## Blockers

- None

## Errors

- None

## Limitations

- This preflight validates one aggregate map/window target in an existing policy report.
- Passing does not make a policy an RL test Bot, content candidate, playtest candidate, or release candidate.
- Any follow-up still requires fixed-window no-regression, target seed checks when relevant, failure-case review, and RL acceptance gates.
