# RL Edge-Aux Staged Opening Handoff Probe

- Gate: `repair`
- Policy kind: `staged_sb3_opening_behavior_clone`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_030_edge_aux_staged_opening_handoff_gap.json`

## Result

The new evaluation path allows `--opening-model` to wrap a `--behavior-clone-model` fallback. This confirms the stage01 opening checkpoint can protect the 60 second opening gate while a behavior clone handles the handoff window.

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 100% | 100% | 100% | watch evidence |
| 180s handoff | 3 | 66.67% | 100% | 66.67% | repair |

The 60 second high-pressure comparison passed across all three maps with no action-bias findings. The 180 second handoff probe still failed on seed `62201` in `soda-creek` at `171.2743s` and `cracked-star-jar` at `157.3380s`. Failure analysis places both deaths in `mid_60_to_180`.

## Interpretation

The blocker has moved from opening retention to mid-window recovery. The opening policy can now be preserved explicitly, but the behavior clone fallback still lacks robust handoff recovery under seed `62201` pressure. This is not RL acceptance and does not permit stage 03.

## Verification

Commands run:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --behavior-clone-model harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/staged.pt --opening-model harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip --opening-seconds 60 --eval-episodes 10 --eval-seconds 60 --seed-start 62400 --rule-bots random,kite,tank --report harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/comparison_60s_10seed.json
```

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --behavior-clone-model harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/staged.pt --opening-model harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip --opening-seconds 60 --eval-episodes 3 --eval-seconds 180 --seed-start 62200 --rule-bots random,kite,tank --report harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/comparison_180s_3seed.json
```

```bash
python3 tools/analyze_rl_policy_failures.py harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/comparison_180s_3seed.json --report harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/failure_analysis_180s.json --markdown harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/failure_analysis_180s.md
```

## Next Step

Run failed-only snapshot traces for `soda-creek` and `cracked-star-jar` seed `62201`, then train or constrain a dedicated handoff/mid fallback. Keep the stage01 opening checkpoint fixed until the handoff fallback passes deterministic 180 second high-pressure comparison.
