# Policy Target Seed Preflight

- Decision: `policy_target_seed_preflight_failed`
- Comparison: `harness/reports/2026-05-30_rl_stage01_seed63402_guard_retention_probe_001/comparison_60s.json`
- Targets: `1`

## Target Results

| Map | Seed | Found | Time | Terminal | Action Ratios |
|---|---:|---|---:|---|---|
| `soda-creek` | `63402` | `True` | `37.4998` | `defeat` | `7=0.0` |

## Blockers

- soda-creek:63402: time_seconds 37.4998 did not reach window 60.0000
- soda-creek:63402: terminal_kind `defeat` is not `victory`
- soda-creek:63402: action 7 ratio 0.000000 below required 0.100000

## Limitations

- This preflight only validates target episodes already present in a comparison report.
- A passing preflight does not replace fixed-window high-pressure comparison, no-regression validation, failure-case review, or RL acceptance.
- Target action ratios are diagnostic checks; they should not be used alone as proof of good play.
