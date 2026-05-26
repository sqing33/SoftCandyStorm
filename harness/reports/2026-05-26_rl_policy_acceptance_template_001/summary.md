# RL Policy Acceptance Validation

- Source: `python/train/rl_policy_acceptance_template.json`
- Policy: `behavior_clone_kite_context3_danger_weighted_smoke`
- Policy type: `behavior_clone`
- Gate decision: `blocked_by_local_binary_launch`
- Decision: `rl_policy_acceptance_not_ready`
- Local binary: `local_binary_launch_blocked`

## Evidence

- training_report_path: `harness/reports/2026-05-26_rl_behavior_clone_kite_context3_danger_weighted_smoke_001/run_output.json`
- short_eval_report_path: `None`
- long_eval_report_path: `None`
- rule_bot_comparison_report_path: `None`
- local_binary_diagnostic_report_path: `harness/reports/2026-05-26_local_binary_launch_diagnostic_001/local_binary_launch_diagnostic.json`
- local_binary_decision: `local_binary_launch_blocked`
- failure_case_count: `2`
- unresolved_failure_case_count: `1`

## Evaluation Reports

| Report | Present | Seconds | Maps | Min win rate | Gate |
|---|---|---:|---:|---:|---|
| `short_eval_report` | False | None | 0 | None | `None` |
| `long_eval_report` | False | None | 0 | None | `None` |
| `rule_bot_comparison_report` | False | None | 0 | None | `None` |

## Blockers

- training_report: gate_decision `behavior_clone_smoke_only_not_policy_gate` is not policy acceptance evidence
- local_binary_diagnostic: decision is `local_binary_launch_blocked`
- short_eval_report: missing comparison/evaluation report
- long_eval_report: missing comparison/evaluation report
- rule_bot_comparison_report: missing comparison/evaluation report

## Errors

- None

## Warnings

- model_metadata_path: missing metadata is allowed only because this is not a candidate

## Limitations

- This validator checks evidence shape and recorded metrics only; it does not run Rust, Gym, Harness, or training.
- An rl_test_bot_candidate decision is still not a fun, balance, playtest, release, or accepted-content gate.
- When local_binary_launch_blocked is active, no RL/Gym comparison depending on game_harness can be promoted.
