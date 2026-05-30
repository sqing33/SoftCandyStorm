# Stage 01 Seed 63402 Edge Recovery Start Alignment

- Decision: `start_policy_anchor_alignment_failed`
- Candidate: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Anchor: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_anchor_001/seed63402_edge_recovery_anchor.pt`
- Scope: offline alignment precheck before another PPO continuation.

## Results

| Dataset | Samples | Mean KL | Argmax Agreement | Decision |
|---|---:|---:|---:|---|
| `edge_recovery_samples.jsonl` | `76` | `2.131519` | `0.0` | `failed` |
| `soda_success_opening_retention_samples.jsonl` | `32` | `0.759214` | `1.0` | `failed` |

## Conclusion

The parent SB3 policy is not a suitable start point for direct edge-recovery-anchor PPO regularization. It completely disagrees with the learned anchor on the edge recovery repair rows, and it is still too high-KL on the retention rows even where the argmax action matches.

The next step should be supervised SB3 initialization / distillation from the edge recovery anchor, or a narrower constrained opening branch, before any further closed-loop PPO probe.

## Validation

- `parent_vs_edge_recovery_anchor_edge_samples.json`: `behavior_clone_anchor_alignment_failed`, mean KL `2.131519`, argmax agreement `0.0`.
- `parent_vs_edge_recovery_anchor_retention_samples.json`: `behavior_clone_anchor_alignment_failed`, mean KL `0.759214`, argmax agreement `1.0`.
- Failure case: `harness/failed_cases/fail_20260530_012_stage01_seed63402_edge_recovery_start_alignment_precheck.json`.
- Validators: `validate_failure_cases.py` passed; docs coverage and roadmap remain incomplete with no errors; progress references are valid; goal consistency is coherent not-ready; blocker audit reports expected blockers; `git diff --check` passed.
