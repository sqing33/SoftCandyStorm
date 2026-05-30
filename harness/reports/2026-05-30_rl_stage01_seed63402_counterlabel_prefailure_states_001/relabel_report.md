# Policy Trace Sample Relabel

- Decision: `policy_trace_samples_relabeled`
- Samples: `48`
- Target actions: `7,3`
- Unchanged: `0`

## Original Actions

| Action | Count | Ratio |
|---|---:|---:|
| `5` | `48` | `1.0` |

## Relabeled Actions

| Action | Count | Ratio |
|---|---:|---:|
| `3` | `24` | `0.5` |
| `7` | `24` | `0.5` |

## Limitations

- Counterfactual labels are design hypotheses, not observed successful actions.
- A dataset produced by this tool must pass dry-run checks, anchor validation, target-seed preflight, fixed-window comparison, and no-regression review before use as policy evidence.
