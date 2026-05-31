# Terminal Conversion Probe Gate

- Decision: `terminal_conversion_probe_failed`
- Target: `caramel-workshop` / `300s`
- Errors: `0`
- Blockers: `4`
- Warnings: `1`

## Target Metrics

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| Win rate | 0.0 | 0.0 | 0.0 |
| Average survival seconds | 231.2871 | 230.8648 | -0.4223 |

## Terminal Usage

- Found terminal branch: `True`
- Map terminal decisions: `832` / `20776` (`0.04`)
- Bucket: `late_180_to_300`
- Bucket terminal decisions: `832` / `4576` (`0.1818`)

## Policy Adapter Scope

- Requirement: `required`
- Scope (required, `terminal`): `policy_adapter_scope_passed`, branch decisions `832`, ratio `0.011266`

## Blockers

- 300s/caramel-workshop: win_rate 0.0000 below required 0.3333
- 300s/caramel-workshop: win_rate delta 0.0000 below required 0.3333
- 300s/caramel-workshop: survival delta -0.4223s below required 0.0000s
- window_regression: expected policy_window_regression_passed, got policy_window_regression_failed

## Errors

- None

## Warnings

- 300s/caramel-workshop: terminal branch was used but produced no victories

## Limitations

- This gate validates terminal-conversion repair evidence only.
- Passing allows limited follow-up consideration, not RL acceptance or release promotion.
- It depends on supplied comparison and no-regression reports; it does not replay episodes by itself.
