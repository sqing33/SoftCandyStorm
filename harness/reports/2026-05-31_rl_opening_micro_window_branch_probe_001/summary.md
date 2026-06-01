# Opening Micro Window Branch Probe

- Decision: `repair_evidence_limited_followup`
- Scope: evaluation-only `edge_recovery_branch`
- Map: `caramel-workshop`
- Branch window: `19.0-19.8s`
- Dispatch guards: `min_pressure=0.2`, `min_boundary_edge_risk=0.75`
- Base model: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/ppo_opening_mid_boundary_retention_seed63405_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`

## Key Results

- Target seed preflight passed: `caramel-workshop:63402` reached `60.0328s` victory with action ratios `5=0.112715` and `7=0.556358`.
- `60s/caramel-workshop` hard preflight passed: win rate `0.6667`, average survival `55.9217s`, normalized action entropy `0.4324`, dominant action `7` ratio `0.6815`.
- High-pressure `60/180/300s` parent no-regression passed with `0` blockers. `caramel-workshop` action distribution L1 deltas were `0.31` at 60s, `0.1817` at 180s, and `0.1889` at 300s.
- Adapter scope passed: only `3` total branch decisions across the three high-pressure comparisons, total branch ratio `0.000027`, all within `opening_lt_60`.
- `63400-63409` caramel 300s follow-up passed versus the base follow-up: win rate stayed `0.1`, average survival improved by `17.195s`, and action distribution L1 delta was `0.037`.
- Edge recovery sample validation passed for the target seed, high-pressure windows, and 10 seed caramel follow-up; the 10 seed follow-up produced one valid sample at seed `63402`.

## Interpretation

The broad `0-60s` opening branch was rejected because rare early dispatches created long-window action distribution drift. This micro-window keeps the same target repair signal for seed `63402` while avoiding that broad-branch drift in the fixed-window and 10 seed follow-up checks.

This is still repair evidence only. It does not promote the wrapper to an RL test Bot, stage 03 candidate, content candidate, playtest candidate, or acceptance policy. The next implementation step should turn this evaluation-only dispatch into a real constrained policy or branch objective, then rerun the same target seed, `60s/caramel-workshop`, high-pressure parent no-regression, adapter scope, and 10 seed caramel follow-up gates.
