# RL Stage 01 Seed 63402 Trace Diagnostic

- Decision: `stage01_seed63402_trace_diagnostic_recorded`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate model: `harness/reports/2026-05-30_rl_current_high_pressure_stage01_seed_replay_probe_001/stage01_seed_replay.zip`
- Map / seeds: `soda-creek`, seeds `63400-63402`
- Duration: `60s`
- Target failure: seed `63402`

## Evidence

| Model | Win rate | seed 63400 | seed 63401 | seed 63402 |
|---|---:|---|---|---|
| parent | `0.6667` | victory `60.0328s` | victory `60.0328s` | defeat `37.3331s` |
| candidate | `0.6667` | victory `60.0328s` | victory `60.0328s` | defeat `37.2664s` |

## Findings

- The seed replay candidate did not materially change the target seed behavior: both parent and candidate keep the same sampled target-seed action mix, with action `5` at `69.91%`, action `2` at `18.58%`, action `4` at `11.50%`, and no sampled action `3` or `7`.
- Successful same-window seeds average action `7` at `56.87%` and action `3` at `15.39%`; seed `63402` is missing both success actions and overuses actions `4` / `5`.
- Candidate seed `63402` enters a continuous sampled action `5` run from `11.3334s` to death at `37.2664s`.
- The first sampled high-pressure boundary frame for candidate seed `63402` appears at `31.9999s`: `boundary_min_distance = 0.0`, `boundary_edge_risk = 1.0`, `enemy_pressure_risk = 0.671`, selected action `5`, top action score `5:0.7658`.
- Low-health risk only appears late at `36.9998s`, when the policy is already stuck on action `5` with an enemy hitbox distance of `0.0`.

## Conclusion

Seed replay alone did not create an opening escape trigger for seed `63402`. The next stage 01 repair should target the long action `5` lock while pinned to the boundary under rising enemy pressure, and should explicitly preserve / encourage the success-seed escape actions `7` and `3` before another 60 / 180 / 300 second parent no-regression run.

## Artifacts

- `parent_trace_evaluation.json`
- `candidate_trace_evaluation.json`
- `parent_traces/`
- `candidate_traces/`
- `trace_comparison.json`
- `trace_comparison.md`
- `parent_route_recovery_hotspots.json`
- `parent_route_recovery_hotspots.md`
- `candidate_route_recovery_hotspots.json`
- `candidate_route_recovery_hotspots.md`
