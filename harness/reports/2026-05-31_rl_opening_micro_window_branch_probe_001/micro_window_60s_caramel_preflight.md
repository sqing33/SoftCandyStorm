# Policy Window Target Preflight

- Decision: `policy_window_target_preflight_passed`
- Comparison: `harness/reports/2026-05-31_rl_opening_micro_window_branch_probe_001/micro_window_high_pressure_60s.json`
- Target: `micro-window-60s` / `caramel-workshop`

## Result

| Metric | Value |
|---|---:|
| Win rate | `0.6667` |
| Average survival seconds | `55.9217` |
| Normalized action entropy | `0.4324` |
| Dominant action ratio | `0.6815` |

## Blockers

- None

## Errors

- None

## Limitations

- This preflight validates one aggregate map/window target in an existing policy report.
- Passing does not make a policy an RL test Bot, content candidate, playtest candidate, or release candidate.
- Any follow-up still requires fixed-window no-regression, target seed checks when relevant, failure-case review, and RL acceptance gates.
