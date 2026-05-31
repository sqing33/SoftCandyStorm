# Policy Adapter Scope Validation

- Decision: `policy_adapter_scope_passed`
- Expected mode: `edge_recovery_branch`
- Comparisons: `3`
- Total branch decisions: `18`
- Total branch ratio: `0.000165`

## Comparisons

| Label | Mode | Branch decisions | Branch ratio |
|---|---|---:|---:|
| `60s` | `edge_recovery_branch` | 4 | 0.0003 |
| `180s` | `edge_recovery_branch` | 7 | 0.0002 |
| `300s` | `edge_recovery_branch` | 7 | 0.0001 |

## Blockers

- None

## Errors

- None

## Limitations

- This gate validates evaluation-only policy adapter scope and provenance only.
- Passing does not make the policy an RL test Bot, content candidate, playtest candidate, or release candidate.
- A policy still requires fixed-window no-regression, target preflights, failure-case review, and RL acceptance gates.
