# Terminal Sequence Late Split Probe

- Decision: `terminal_only_split_failed_no_conversion`
- Scope: evaluation-only map late split using the per-map chain parent as base and the `terminal-sequence-recovery` checkpoint only after `180s` on `caramel-workshop`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Late split model: `harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Split: `caramel-workshop` at `180s`
- Wrapper stack: per-map edge branch, all-map late recovery filter
- Baseline: `harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/`
- Failure case: `harness/failed_cases/fail_20260531_005_terminal_sequence_opening_preservation_tradeoff.json`

## Fixed Window Result

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---:|---:|---:|---:|---|
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `1.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_not_balance_gate` |

`window_regression_vs_per_map_chain.json` failed with one blocker:

- `300s/caramel-workshop`: average survival `-2.4116s`

## Interpretation

The late split preserves the 60s and 180s windows exactly and avoids disturbing `soda-creek` or `cracked-star-jar` at 300s, but it does not produce the raw terminal-sequence checkpoint's `caramel-workshop` seed `63402` conversion. Switching only after `180s` leaves `caramel-workshop` at `0.0` win rate and slightly below the per-map chain baseline survival.

This suggests the terminal-sequence checkpoint's positive signal is not a simple terminal-only action patch. Its winning `caramel-workshop` trajectory depends on earlier closed-loop state evolution, while its short-window regression shows that full-policy replacement is also unsafe.

## Validation

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_per_map_chain.json`

## Limitations

- This is evaluation-only split-policy evidence, not a trained policy candidate.
- The candidate failed no-regression and must not be used as a stage 03 model, RL test Bot, balance gate, playtest gate, or release evidence.
