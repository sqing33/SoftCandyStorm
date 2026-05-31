# Policy Target Seed Preflight

- Decision: `policy_target_seed_preflight_passed`
- Comparison: `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/candidate_caramel_300s_10seed.json`
- Targets: `1`

## Target Results

| Map | Seed | Found | Time | Terminal | Action Ratios |
|---|---:|---|---:|---|---|
| `caramel-workshop` | `63407` | `True` | `300.0150` | `victory` | `` |

## Limitations

- This preflight only validates target episodes already present in a comparison report.
- A passing preflight does not replace fixed-window high-pressure comparison, no-regression validation, failure-case review, or RL acceptance.
- Target action ratios are diagnostic checks; they should not be used alone as proof of good play.
