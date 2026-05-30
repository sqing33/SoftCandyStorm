# Stage 01 Seed 63402 Edge Recovery Supervised Init

- Decision: `teacher_probs_supervised_init_alignment_failed_not_policy_gate`
- Model: `seed63402_edge_recovery_supervised_init.zip`
- Teacher: `seed63402_edge_recovery_anchor.pt`
- Target mode: `teacher_probs`
- Samples: `108` edge recovery + retention rows.

## Results

| Check | Result |
|---|---|
| Distillation validation argmax accuracy | `0.8636` |
| Action distribution guard | `passed` |
| Combined anchor alignment | `failed`, mean KL `0.674023`, argmax agreement `0.8796` |
| Edge rows alignment | `failed`, mean KL `0.744349`, argmax agreement `0.8289` |
| Retention rows alignment | `failed`, mean KL `0.506999`, argmax agreement `1.0` |

## Conclusion

The teacher-probs supervised initialization improved the parent mismatch but remained too high-KL against the edge recovery anchor. It did not qualify for target-seed preflight or PPO follow-up.

The next variant used `dataset_actions` hard labels to reduce KL and is documented in `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/summary.md`.
