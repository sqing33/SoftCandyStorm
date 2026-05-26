# RL Policy Acceptance Validation

- Source: `python/train/rl_policy_acceptance_gru_context8_entropy002.json`
- Policy: `behavior_clone_kite_gru_context8_entropy002`
- Policy type: `behavior_clone`
- Gate decision: `repair`
- Decision: `rl_policy_acceptance_not_ready`
- Local binary: `local_binary_launch_ok`

## Evidence

- training_report_path: `harness/reports/2026-05-27_rl_behavior_clone_kite_gru_context8_entropy002_smoke_001/run_output.json`
- short_eval_report_path: `harness/reports/2026-05-27_rl_behavior_clone_kite_gru_context8_entropy002_multimap_60s_001/comparison.json`
- long_eval_report_path: `harness/reports/2026-05-27_rl_behavior_clone_kite_gru_context8_entropy002_multimap_300s_001/comparison.json`
- rule_bot_comparison_report_path: `harness/reports/2026-05-27_rl_behavior_clone_kite_gru_context8_entropy002_multimap_300s_001/comparison.json`
- local_binary_diagnostic_report_path: `harness/reports/2026-05-27_local_binary_launch_diagnostic_after_devtools_terminal_001/local_binary_launch_diagnostic.json`
- local_binary_decision: `local_binary_launch_ok`
- failure_case_count: `1`
- unresolved_failure_case_count: `1`

## Evaluation Reports

| Report | Present | Seconds | Maps | Min win rate | Gate |
|---|---|---:|---:|---:|---|
| `short_eval_report` | True | 60.0 | 3 | 0.8 | `multimap_comparison_recorded_not_balance_gate` |
| `long_eval_report` | True | 300.0 | 3 | 0.0 | `multimap_comparison_recorded_needs_policy_repair` |
| `rule_bot_comparison_report` | True | 300.0 | 3 | 0.0 | `multimap_comparison_recorded_needs_policy_repair` |

## Blockers

- training_report: gate_decision `behavior_clone_smoke_only_not_policy_gate` is not policy acceptance evidence
- short_eval_report: minimum policy win rate must be >= 1, got `0.8`
- short_eval_report.soda-creek: policy win rate 0.8 is below best rule Bot 1
- short_eval_report.cracked-star-jar: policy win rate 0.8 is below best rule Bot 1
- long_eval_report: minimum policy win rate must be >= 1, got `0.0`
- long_eval_report: report gate_decision `multimap_comparison_recorded_needs_policy_repair` still indicates repair/watch
- long_eval_report: report still contains 2 finding(s)
- long_eval_report.soda-creek: policy win rate 0 is below best rule Bot 0.667
- long_eval_report.cracked-star-jar: policy win rate 0 is below best rule Bot 1
- rule_bot_comparison_report: minimum policy win rate must be >= 1, got `0.0`
- rule_bot_comparison_report: report gate_decision `multimap_comparison_recorded_needs_policy_repair` still indicates repair/watch
- rule_bot_comparison_report: report still contains 2 finding(s)
- rule_bot_comparison_report.soda-creek: policy win rate 0 is below best rule Bot 0.667
- rule_bot_comparison_report.cracked-star-jar: policy win rate 0 is below best rule Bot 1

## Errors

- None

## Warnings

- model_metadata_path: missing metadata is allowed only because this is not a candidate

## Limitations

- This validator checks evidence shape and recorded metrics only; it does not run Rust, Gym, Harness, or training.
- An rl_test_bot_candidate decision is still not a fun, balance, playtest, release, or accepted-content gate.
- When local_binary_launch_blocked is active, no RL/Gym comparison depending on game_harness can be promoted.
