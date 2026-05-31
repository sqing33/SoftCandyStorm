# Terminal Sequence Staged Opening Probe

- Decision: `opening_preservation_diagnostic_failed_terminal_signal_removed`
- Scope: evaluation-only staged opening wrapper for the `terminal-sequence-recovery` checkpoint
- Base opening model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Fallback model after `60s`: `harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Wrapper stack: staged opening, per-map edge branch, all-map late recovery filter
- Baseline: `harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/`
- Failure case: `harness/failed_cases/fail_20260531_005_terminal_sequence_opening_preservation_tradeoff.json`

## Fixed Window Result

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---:|---:|---:|---:|---|
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `1.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_not_balance_gate` |

The staged opening wrapper repaired the earlier 60s caramel opening regression, but it also removed the useful 300s conversion signal from the raw terminal-sequence checkpoint. `window_regression_vs_per_map_chain.json` failed with two 300s survival blockers:

- `caramel-workshop`: average survival `-1.6003s`
- `cracked-star-jar`: average survival `-19.3985s`

## Interpretation

The raw terminal-sequence checkpoint won `caramel-workshop` seed `63402` and all three `cracked-star-jar` 300s episodes, but only after allowing the checkpoint to control the earlier trajectory. Replacing the first `60s` with the parent opening policy kept the short-window gate intact, yet `caramel-workshop` seed `63402` died at `244.0232s` and `cracked-star-jar` seeds `63400` / `63401` also regressed.

This means a coarse 0-60s staged opening wrapper is too blunt. The next probe needs a selective opening-preservation guard that protects the failing `caramel-workshop` opening case without erasing the terminal-sequence trajectory that made seed `63402` convertible, or a training-time hard guard that rejects the checkpoint as soon as 60s caramel regresses.

## Validation

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_per_map_chain.json`

## Limitations

- This is evaluation-only wrapper evidence, not a trained policy candidate.
- The candidate failed no-regression and must not be used as a stage 03 model, RL test Bot, balance gate, playtest gate, or release evidence.
