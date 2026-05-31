# Policy Target Seed Preflight

- Decision: `policy_target_seed_preflight_failed`
- Comparison: `harness/reports/2026-05-31_rl_failure_lane_opening_repair_branch_preflight_001/opening_branch_target_comparison_60s_window30_55.json`
- Targets: `1`

## Target Results

| Map | Seed | Found | Time | Terminal | Action Ratios |
|---|---:|---|---:|---|---|
| `caramel-workshop` | `63402` | `True` | `60.0328` | `victory` | `5=0.308162, 7=0.350916` |

## Blockers

- caramel-workshop:63402: action 5 ratio 0.308162 above allowed 0.300000

## Limitations

- This preflight only validates target episodes already present in a comparison report.
- A passing preflight does not replace fixed-window high-pressure comparison, no-regression validation, failure-case review, or RL acceptance.
- Target action ratios are diagnostic checks; they should not be used alone as proof of good play.
