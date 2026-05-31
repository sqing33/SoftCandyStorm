# Policy Window Target Preflight

- Decision: `policy_window_target_preflight_failed`
- Comparison: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/candidate_high_pressure_60s.json`
- Target: `60s-caramel-short-window` / `caramel-workshop`

## Result

| Metric | Value |
|---|---:|
| Win rate | `0.3333` |
| Average survival seconds | `49.2774` |
| Normalized action entropy | `0.5387` |
| Dominant action ratio | `0.5475` |

## Blockers

- 60s-caramel-short-window/caramel-workshop: win_rate 0.3333 below required 0.6667
- 60s-caramel-short-window/caramel-workshop: average_survival_seconds 49.2774 below required 55.0000

## Errors

- None

## Limitations

- This preflight validates one aggregate map/window target in an existing policy report.
- Passing does not make a policy an RL test Bot, content candidate, playtest candidate, or release candidate.
- Any follow-up still requires fixed-window no-regression, target seed checks when relevant, failure-case review, and RL acceptance gates.
