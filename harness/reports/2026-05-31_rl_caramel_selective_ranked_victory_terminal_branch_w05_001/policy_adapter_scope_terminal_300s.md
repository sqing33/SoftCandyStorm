# Policy Adapter Scope Validation

- Decision: `policy_adapter_scope_passed`
- Expected mode: `terminal_conversion_branch`
- Comparisons: `1`
- Total branch decisions: `832`
- Total branch ratio: `0.011266`

## Comparisons

| Label | Mode | Branch decisions | Branch ratio |
|---|---|---:|---:|
| `300s` | `terminal_conversion_branch` | 832 | 0.011266 |

## Blockers

- None

## Errors

- None

## Limitations

- This gate validates evaluation-only policy adapter scope and provenance only.
- Passing does not make the policy an RL test Bot, content candidate, playtest candidate, or release candidate.
- A policy still requires fixed-window no-regression, target preflights, failure-case review, and RL acceptance gates.
