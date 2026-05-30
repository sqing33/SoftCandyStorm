# Policy Target Seed Preflight

- Decision: `policy_target_seed_preflight_passed`
- Comparison: `harness/reports/2026-05-30_rl_caramel_opening_edge_branch_probe_001/caramel_branch_comparison_60s.json`
- Targets: `1`

## Target Results

| Map | Seed | Found | Time | Terminal | Action Ratios |
|---|---:|---|---:|---|---|
| `caramel-workshop` | `63402` | `True` | `60.0328` | `victory` | `5=0.208218, 7=0.38201` |

## Limitations

- This preflight only validates target episodes already present in a comparison report.
- A passing preflight does not replace fixed-window high-pressure comparison, no-regression validation, failure-case review, or RL acceptance.
- Target action ratios are diagnostic checks; they should not be used alone as proof of good play.
