# Progress Report Reference Validation

- Source: `harness/progress.json`
- Decision: `progress_reports_valid`
- Items: 220
- Report references: 172 / 172
- Items without report: 45

## Sections

| Section | Items |
|---|---:|
| `completed` | 145 |
| `current_findings` | 72 |
| `next_recommended` | 3 |

## Errors

- None

## Warnings

- rl_dqn_training_smoke: no report evidence path recorded
- rl_policy_rule_bot_comparison: no report evidence path recorded
- rl_policy_observability_fields: no report evidence path recorded
- rl_training_metadata_isolation: no report evidence path recorded
- rl_ppo_training_smoke: no report evidence path recorded
- rl_action_bias_gate: no report evidence path recorded
- rl_dqn_action_bias_repair_experiment: no report evidence path recorded
- rl_reward_shaping_action_bias_repair: no report evidence path recorded
- rl_reward_shaping_ppo_comparison: no report evidence path recorded
- rl_policy_extended_comparison: no report evidence path recorded
- rl_ppo_multimap_extended_comparison: no report evidence path recorded
- rl_ppo_multimap_training_experiment: no report evidence path recorded
- rl_ppo_multimap_random_training_experiment: no report evidence path recorded
- rl_ppo_multimap_entropy_experiment: no report evidence path recorded
- rl_ppo_stochastic_eval_diagnostic: no report evidence path recorded
- rl_ppo_repeat_penalty_experiment: no report evidence path recorded
- rl_ppo_repeat_penalty_stochastic_diagnostic: no report evidence path recorded
- rl_ppo_repeat_penalty_longer_training: no report evidence path recorded
- rl_ppo_longer_training_stochastic_diagnostic: no report evidence path recorded
- rl_ppo_repeat_penalty_100k_training_gate: no report evidence path recorded
- rl_ppo_100k_multimap_comparison: no report evidence path recorded
- rl_policy_action_score_diagnostic: no report evidence path recorded
- rl_ppo_100k_action_score_multimap_diagnostic: no report evidence path recorded
- rl_observation_v2: no report evidence path recorded
- rl_ppo_observation_v2_training_baseline: no report evidence path recorded
- rl_ppo_observation_v2_multimap_comparison: no report evidence path recorded
- rl_ppo_observation_v2_50k_training: no report evidence path recorded
- rl_ppo_observation_v2_50k_multimap_comparison: no report evidence path recorded
- rl_training_episode_controls: no report evidence path recorded
- rl_multimap_comparison_entrypoint: no report evidence path recorded
- rl_ppo_observation_v2_high_pressure_train300_50k_training: no report evidence path recorded
- rl_ppo_observation_v2_high_pressure_train300_50k_comparison: no report evidence path recorded
- rl_reward_safety_shaping: no report evidence path recorded
- rl_ppo_observation_v2_high_pressure_safety_train300_50k_training: no report evidence path recorded
- rl_ppo_observation_v2_high_pressure_safety_train300_50k_comparison: no report evidence path recorded
- rl_reward_safety_delta_available: no report evidence path recorded
- rl_ppo_safety_delta_train300_action_bias: no report evidence path recorded
- rl_ppo_safety_delta_stochastic_gap: no report evidence path recorded
- rl_warm_start_training_available: no report evidence path recorded
- rl_ppo_warm_start_safety_delta_action_gate: no report evidence path recorded
- rl_ppo_warm_start_safety_delta_high_pressure_watch: no report evidence path recorded
- rl_training_eval_map_available: no report evidence path recorded
- rl_ppo_soda_focus_warm_start_action_gate: no report evidence path recorded
- rl_ppo_soda_focus_warm_start_regression: no report evidence path recorded
- rl_rule_bot_trajectory_export_available: no report evidence path recorded
- progress id `rl_reward_safety_delta_available` appears in multiple sections: completed[122], current_findings[48]
- progress id `rl_ppo_safety_delta_train300_action_bias` appears in multiple sections: completed[123], current_findings[49]
- progress id `rl_ppo_safety_delta_stochastic_gap` appears in multiple sections: completed[124], current_findings[50]
- progress id `rl_warm_start_training_available` appears in multiple sections: completed[125], current_findings[51]
- progress id `rl_ppo_warm_start_safety_delta_action_gate` appears in multiple sections: completed[126], current_findings[52]
- progress id `rl_ppo_warm_start_safety_delta_high_pressure_watch` appears in multiple sections: completed[127], current_findings[53]
- progress id `rl_training_eval_map_available` appears in multiple sections: completed[128], current_findings[54]
- progress id `rl_ppo_soda_focus_warm_start_action_gate` appears in multiple sections: completed[129], current_findings[55]
- progress id `rl_ppo_soda_focus_warm_start_regression` appears in multiple sections: completed[130], current_findings[56]
- progress id `rl_rule_bot_trajectory_export_available` appears in multiple sections: completed[131], current_findings[57]

## Limitations

- This validator checks progress ledger structure and local report path existence only.
- It does not prove the referenced report's conclusions are correct or still current.
- Older completed entries without a report are warnings, not errors, until backfilled.
