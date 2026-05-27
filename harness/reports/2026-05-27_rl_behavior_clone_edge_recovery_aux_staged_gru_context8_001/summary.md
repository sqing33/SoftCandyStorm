# RL Behavior Clone Edge Recovery Auxiliary Staged GRU Context8

- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_edge_recovery_aux_staged_gru_context8_001/staged.pt`
- Training data: phase-aligned high-pressure KiteBot trajectories plus `2215` edge recovery supervision samples
- Edge recovery sample weight: `4.0`
- Failure case: `harness/failed_cases/fail_20260527_028_edge_recovery_aux_opening_regression.json`

## Dataset

The combined dry-run contains `23941` movement samples: `21726` trajectory samples and `2215` `edge_recovery_supervision` repair samples. Sequence diagnostics reported no flags before training.

## Phase Training

| Phase | Samples | Edge samples | Validation accuracy | Validation entropy | Edge weighted train ratio |
|---|---:|---:|---:|---:|---:|
| `opening` | 5591 | 203 | 0.8166 | 0.811745 | 0.0376 |
| `mid` | 10883 | 972 | 0.8397 | 0.735273 | 0.0910 |
| `late` | 7467 | 1040 | 0.8125 | 0.687818 | 0.1374 |

## 60 Second Gate

The 60 second high-pressure comparison used `10` seeds starting at `62400`. It failed the required opening gate: `soda-creek` reached only `40%` win rate, with action `3` covering `87.27%` of policy steps and action entropy `0.7851` bits. `caramel-workshop` reached `90%`; `cracked-star-jar` reached `70%`.

Because the 60 second gate failed, the 180 second staged handoff comparison was not run. This candidate is repair evidence only and cannot proceed to stage 03 or RL policy acceptance.

## Next

Do not keep increasing the same mixed clone unchanged. The next repair should address opening action `3` collapse first, then rerun the 60 second gate before any 180 second handoff comparison.
