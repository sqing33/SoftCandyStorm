# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `16`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/ppo_training_report.json`
- Anchor alignment: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/anchor_alignment.json`
- Window regression: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/window_regression_vs_anchor_regularized_smoke.json`
- Window regression: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/window_regression_vs_current_failure_best.json`
- Window regression: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/window_regression_vs_seed63100_stage02.json`
- Failure analysis: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/failure_analysis_300s.json`

## Blockers

- anchor_alignment: overall mean_kl 0.34314 exceeds 0.25
- anchor_alignment: overall argmax_agreement 0.6966 below 0.75
- anchor_alignment: by_map/soda-creek: mean_kl 0.369067 exceeds 0.35
- anchor_alignment: by_time_bucket/mid_60_to_180: mean_kl 0.431042 exceeds 0.35
- window_regression_vs_anchor_regularized_smoke: 180/soda-creek: win_rate_delta -0.3334 below required 0.0
- window_regression_vs_anchor_regularized_smoke: 180/soda-creek: average_survival_seconds dropped 12.0816s beyond allowed 0.0s
- window_regression_vs_anchor_regularized_smoke: 300/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- window_regression_vs_anchor_regularized_smoke: 300/cracked-star-jar: average_survival_seconds dropped 8.8419s beyond allowed 0.0s
- window_regression_vs_anchor_regularized_smoke: 300/soda-creek: average_survival_seconds dropped 29.842s beyond allowed 0.0s
- window_regression_vs_current_failure_best: 180/cracked-star-jar: average_survival_seconds dropped 4.8339s beyond allowed 0.0s
- window_regression_vs_current_failure_best: 180/soda-creek: average_survival_seconds dropped 26.4024s beyond allowed 0.0s
- window_regression_vs_current_failure_best: 300/caramel-workshop: average_survival_seconds dropped 6.8348s beyond allowed 0.0s
- window_regression_vs_current_failure_best: 300/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- window_regression_vs_current_failure_best: 300/cracked-star-jar: average_survival_seconds dropped 25.5538s beyond allowed 0.0s
- window_regression_vs_current_failure_best: 300/soda-creek: average_survival_seconds dropped 33.7396s beyond allowed 0.0s
- window_regression_vs_seed63100_stage02: 300/cracked-star-jar: average_survival_seconds dropped 5.4463s beyond allowed 0.0s

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
