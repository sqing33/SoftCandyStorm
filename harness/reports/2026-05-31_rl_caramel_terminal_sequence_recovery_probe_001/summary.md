# Caramel Terminal Sequence Recovery Probe

- Decision: `rl_repair_probe_gate_failed_opening_regression`
- Scope: guarded PPO continuation with `terminal-sequence-recovery`, wrapped by the current per-map edge branch plus all-map late recovery filter for fixed-window comparison
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate model: `harness/reports/2026-05-31_rl_caramel_terminal_sequence_recovery_probe_001/ppo_caramel_terminal_sequence_recovery_probe.zip`
- Training map / seeds: `caramel-workshop`, seeds `63400-63402`
- Timesteps: requested `256`, actual `256`
- Failure case: `harness/failed_cases/fail_20260531_004_terminal_sequence_recovery_opening_regression.json`

## Training Result

The probe trained with the new `terminal-sequence-recovery` reward profile and behavior-clone anchor regularization. The anchor guard passed:

- Final validation mean KL: `0.106769`
- Final argmax agreement: `0.8251`
- Guard decision: `anchor_validation_guard_passed`

The training-time 60s caramel-workshop evaluation reached `1.0` win rate, but that short self-check did not hold once the model was evaluated across the full high-pressure wrapper chain and fixed windows.

## Fixed Window Result

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---:|---:|---:|---:|---|
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `1.0` | `0.3333` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |

Compared with the per-map chain baseline, the 300s window improved:

- `caramel-workshop`: win rate `+0.3333`, average survival `+17.0636s`
- `cracked-star-jar`: win rate `+0.6667`, average survival `+10.2753s`
- `soda-creek`: unchanged at `1.0`

However, `window_regression_vs_per_map_chain.json` failed because the 60s caramel-workshop opening regressed:

- win rate delta `-0.3333`
- average survival delta `-4.1111s`

## Interpretation

The new sequence objective is useful signal: unlike the supervised terminal branch probes, it produced an online 300s caramel conversion on the target seed set and improved cracked-star-jar. But it also perturbed the early caramel opening window, so it cannot be promoted.

The next attempt should keep the terminal sequence objective but isolate it from opening behavior. Good options are a staged opening-preservation wrapper, a terminal-only branch trained with `terminal-sequence-recovery`-style objective, or an online guard that hard-stops when the 60s caramel opening gate regresses.

## Validation

- `ppo_training_report.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_per_map_chain.json`
- `harness/failed_cases/fail_20260531_004_terminal_sequence_recovery_opening_regression.json`

## Limitations

- This is a smoke-scale 3-seed repair probe.
- The comparison still uses deterministic wrapper diagnostics and is not RL acceptance evidence.
- The candidate failed no-regression and must not be used as a policy candidate, stage 03 model, RL test Bot, balance gate, playtest gate, or release evidence.
