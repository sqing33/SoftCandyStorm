# Policy Target Seed Preflight

- Decision: `policy_target_seed_preflight_failed`
- Comparison: `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/candidate_caramel_300s_10seed.json`
- Targets: `1`

## Target Results

| Map | Seed | Found | Time | Terminal | Action Ratios |
|---|---:|---|---:|---|---|
| `caramel-workshop` | `63405` | `True` | `138.6673` | `defeat` | `` |

## Blockers

- caramel-workshop:63405: time_seconds 138.6673 below required 180.0000
- caramel-workshop:63405: terminal_kind is `defeat`

## Limitations

- This preflight only validates target episodes already present in a comparison report.
- A passing preflight does not replace fixed-window high-pressure comparison, no-regression validation, failure-case review, or RL acceptance.
- Target action ratios are diagnostic checks; they should not be used alone as proof of good play.
