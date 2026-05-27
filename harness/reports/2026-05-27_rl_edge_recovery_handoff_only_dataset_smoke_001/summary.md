# RL Edge Recovery Handoff-Only Dataset Smoke

- Gate: `dataset_validated_not_training_gate`
- Scope: behavior clone dataset plumbing only
- Opening dry-run: `opening_dry_run.json`
- Mid dry-run: `mid_dry_run.json`

## Result

This smoke validates the new edge recovery time-window filter for staged behavior clone repair. The filter applies only to `edge_recovery_supervision_sample` rows and leaves regular KiteBot trajectory samples untouched.

| Dry run | Time phase | Samples | Edge recovery samples | Source mix |
|---|---|---:|---:|---|
| `opening_dry_run.json` | `opening` | 5388 | 0 | trajectory 100.00% |
| `mid_dry_run.json` | `mid` | 10710 | 799 | trajectory 92.54%, edge recovery 7.46% |

The input set originally contained 2215 edge recovery repair samples. With `--edge-recovery-min-seconds 60`, the loader dropped 376 pre-handoff repair samples before phase filtering. The opening phase then contained no edge recovery rows, while the mid phase retained 799 handoff-window repair rows.

## Commands

Opening dry-run:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py --dry-run --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001/kite_soda_creek.jsonl --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001/kite_caramel_workshop.jsonl --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001/kite_cracked_star_jar.jsonl --dataset harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_samples_001/edge_recovery_samples.jsonl --architecture gru --context-frames 8 --map-conditioning one_hot --time-phase-filter opening --edge-recovery-min-seconds 60 --report harness/reports/2026-05-27_rl_edge_recovery_handoff_only_dataset_smoke_001/opening_dry_run.json
```

Mid dry-run:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py --dry-run --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001/kite_soda_creek.jsonl --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001/kite_caramel_workshop.jsonl --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001/kite_cracked_star_jar.jsonl --dataset harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_samples_001/edge_recovery_samples.jsonl --architecture gru --context-frames 8 --map-conditioning one_hot --time-phase-filter mid --edge-recovery-min-seconds 60 --edge-recovery-max-seconds 180 --report harness/reports/2026-05-27_rl_edge_recovery_handoff_only_dataset_smoke_001/mid_dry_run.json
```

## Limitations

- This is a dataset smoke, not a trained policy.
- It does not satisfy deterministic 60 second high-pressure gate, 180 second handoff compare, 300 second long-run compare, or RL policy acceptance.
- The next policy experiment must keep stage01 opening retention explicit and train or evaluate the handoff window separately.
