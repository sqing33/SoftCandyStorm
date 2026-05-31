# RL Opening Broad Branch Drift Diagnostic

- Decision: `opening_broad_branch_drift_confirmed`
- Lane: `opening_repair`
- Map / seeds: `caramel-workshop:63400-63402`
- Base model: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/ppo_opening_mid_boundary_retention_seed63405_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Gate conclusion: `repair`

## Results

| Seed | Base result | Branch result | Branch decisions | Key action delta | Interpretation |
|---:|---|---|---:|---|---|
| `63400` | `214.6502s` defeat | `214.6502s` defeat | `0` | no sampled divergence | Control seed unchanged. |
| `63401` | `212.3497s` defeat | `221.1183s` defeat | `2` | sampled action `5` ratio `+0.5199` | Two early dispatches push the later trajectory into a long action `5` attractor. |
| `63402` | `40.0997s` defeat | `212.0497s` defeat | `1` | sampled action `5` ratio `-0.4005`, action `7` ratio `+0.2339` | The target seed is repaired past opening death, but still dies late and contributes longer-window drift. |

The branch used only `3 / 19433` decisions (`0.0002`) in this single-map 300s diagnostic, all in `opening_lt_60`. The emitted adapter samples are valid `edge_recovery_supervision_sample` rows and occur at `6.6333s`, `19.5334s`, and `20.0s`; no mid or late branch decisions were recorded.

## Branch Samples

| Seed | Time | Original -> Target | Pressure | Boundary | Notes |
|---:|---:|---|---:|---:|---|
| `63401` | `6.6333s` | `2 -> 3` | `0.2527` | `0.8214` | Early top-edge hazard-pressure dispatch; first sampled divergence. |
| `63401` | `20.0s` | `5 -> 7` | `0.2220` | `1.0` | Bottom-edge action `5` escape, followed by later action `5` dominance. |
| `63402` | `19.5334s` | `5 -> 7` | `0.2157` | `1.0` | Target seed opening rescue; extends episode by `171.95s` but does not convert to win. |

## Interpretation

The `0-60s` broad branch is not failing because it overuses the branch. It fails because extremely sparse early interventions can put nearby seeds onto different closed-loop trajectories. For `63401`, two early dispatches are enough to turn the later sampled action mix from a balanced base distribution into action `5` dominance (`56.93%` sampled ratio in the branch trace). For `63402`, the single dispatch solves the immediate opening death but creates a much longer failed episode whose later action mix still contains substantial action `5`.

This explains the previously recorded parent no-regression blockers: the branch improves the short target lane but does not preserve the parent policy shape at `180s` and `300s`. The next repair should not run a 10 seed follow-up from this broad branch. It should either narrow dispatch with seed/state-specific conditions that exclude `63401`-style early top-edge intervention, or add an online action-distribution / path-retention guard before any promotion attempt.

## Evidence

- `base_caramel_300s_eval.json`
- `branch_caramel_300s_eval.json`
- `base_vs_branch_trace_compare.json`
- `base_vs_branch_trace_compare.md`
- `branch_edge_samples.jsonl`
- `branch_edge_samples_validation.json`
- `branch_edge_samples_validation.md`

## Limitations

- This report compares sampled traces at stride `5`; unsampled frames are not inspected.
- This is diagnostic evidence only. It does not approve an RL policy, stage 03 checkpoint, test Bot, or acceptance candidate.
- The existing fixed-window no-regression failure remains authoritative for rejecting this branch.
