# RL Policy Acceptance Validation

- Source: `python/train/rl_policy_acceptance_ppo_bc_distilled_warmstart.json`
- Policy: `ppo_bc_distilled_warmstart`
- Policy type: `ppo`
- Gate decision: `repair`
- Decision: `rl_policy_acceptance_not_ready`
- Local binary: `local_binary_launch_ok`

## Evidence

- training_report_path: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_001/run_output.json`
- short_eval_report_path: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_multimap_60s_001/comparison.json`
- long_eval_report_path: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_multimap_300s_001/comparison.json`
- rule_bot_comparison_report_path: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_multimap_300s_001/comparison.json`
- local_binary_diagnostic_report_path: `harness/reports/2026-05-27_local_binary_launch_diagnostic_after_terminal_devtools_restart_001/local_binary_launch_diagnostic.json`
- local_binary_decision: `local_binary_launch_ok`
- failure_case_count: `1`
- unresolved_failure_case_count: `1`

## Evaluation Reports

| Report | Present | Seconds | Maps | Min win rate | Gate |
|---|---|---:|---:|---:|---|
| `short_eval_report` | True | 60.0 | 3 | 0.4 | `multimap_comparison_recorded_needs_policy_repair` |
| `long_eval_report` | True | 300.0 | 3 | 0.0 | `multimap_comparison_recorded_needs_policy_repair` |
| `rule_bot_comparison_report` | True | 300.0 | 3 | 0.0 | `multimap_comparison_recorded_needs_policy_repair` |

## Blockers

- short_eval_report: minimum policy win rate must be >= 1, got `0.4`
- short_eval_report: report gate_decision `multimap_comparison_recorded_needs_policy_repair` still indicates repair/watch
- short_eval_report: report still contains 4 finding(s)
- short_eval_report.soda-creek: normalized action entropy 0.1949 is below 0.5
- short_eval_report.soda-creek: dominant action ratio 0.8468 is above 0.7
- short_eval_report.soda-creek: policy win rate 0.4 is below best rule Bot 1
- short_eval_report.caramel-workshop: normalized action entropy 0.1359 is below 0.5
- short_eval_report.caramel-workshop: dominant action ratio 0.912 is above 0.7
- short_eval_report.caramel-workshop: policy win rate 0.8 is below best rule Bot 1
- short_eval_report.cracked-star-jar: normalized action entropy 0.2134 is below 0.5
- short_eval_report.cracked-star-jar: dominant action ratio 0.8232 is above 0.7
- short_eval_report.cracked-star-jar: policy win rate 0.8 is below best rule Bot 1
- long_eval_report: minimum policy win rate must be >= 1, got `0.0`
- long_eval_report: report gate_decision `multimap_comparison_recorded_needs_policy_repair` still indicates repair/watch
- long_eval_report: report still contains 6 finding(s)
- long_eval_report.soda-creek: normalized action entropy 0.2439 is below 0.5
- long_eval_report.soda-creek: dominant action ratio 0.7728 is above 0.7
- long_eval_report.soda-creek: policy win rate 0 is below best rule Bot 0.333
- long_eval_report.caramel-workshop: normalized action entropy 0.3003 is below 0.5
- long_eval_report.caramel-workshop: dominant action ratio 0.7631 is above 0.7
- long_eval_report.caramel-workshop: policy win rate 0 is below best rule Bot 0.333
- long_eval_report.cracked-star-jar: normalized action entropy 0.1928 is below 0.5
- long_eval_report.cracked-star-jar: dominant action ratio 0.8494 is above 0.7
- long_eval_report.cracked-star-jar: policy win rate 0 is below best rule Bot 0.667
- rule_bot_comparison_report: minimum policy win rate must be >= 1, got `0.0`
- rule_bot_comparison_report: report gate_decision `multimap_comparison_recorded_needs_policy_repair` still indicates repair/watch
- rule_bot_comparison_report: report still contains 6 finding(s)
- rule_bot_comparison_report.soda-creek: normalized action entropy 0.2439 is below 0.5
- rule_bot_comparison_report.soda-creek: dominant action ratio 0.7728 is above 0.7
- rule_bot_comparison_report.soda-creek: policy win rate 0 is below best rule Bot 0.333
- rule_bot_comparison_report.caramel-workshop: normalized action entropy 0.3003 is below 0.5
- rule_bot_comparison_report.caramel-workshop: dominant action ratio 0.7631 is above 0.7
- rule_bot_comparison_report.caramel-workshop: policy win rate 0 is below best rule Bot 0.333
- rule_bot_comparison_report.cracked-star-jar: normalized action entropy 0.1928 is below 0.5
- rule_bot_comparison_report.cracked-star-jar: dominant action ratio 0.8494 is above 0.7
- rule_bot_comparison_report.cracked-star-jar: policy win rate 0 is below best rule Bot 0.667

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks evidence shape and recorded metrics only; it does not run Rust, Gym, Harness, or training.
- An rl_test_bot_candidate decision is still not a fun, balance, playtest, release, or accepted-content gate.
- When local_binary_launch_blocked is active, no RL/Gym comparison depending on game_harness can be promoted.
