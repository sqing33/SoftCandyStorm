# Policy Adapter Scope Validation

- Decision: `policy_adapter_scope_passed`
- Expected mode: `health_retention_guard`
- Comparisons: `3`
- Total branch decisions: `0`
- Total branch ratio: `0.0`

## Comparisons

| Label | Mode | Branch decisions | Branch ratio |
|---|---|---:|---:|
| `60s` | `health_retention_guard` | 0 | 0.0 |
| `180s` | `health_retention_guard` | 0 | 0.0 |
| `300s` | `health_retention_guard` | 0 | 0.0 |

## Blockers

- None

## Errors

- None

## Limitations

- This gate validates evaluation-only policy adapter scope and provenance only.
- Passing does not make the policy an RL test Bot, content candidate, playtest candidate, or release candidate.
- A policy still requires fixed-window no-regression, target preflights, failure-case review, and RL acceptance gates.
