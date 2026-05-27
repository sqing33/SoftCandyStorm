# RL Curriculum Stage 02 Stochastic Handoff Probe

- Decision: `stage02_staged_opening_stochastic_probe_recorded`
- Deterministic reference: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_trace_001/summary.md`
- Evaluation: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_stochastic_probe_001/evaluation_with_trace.json`
- Trace: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_stochastic_probe_001/traces/soda-creek_seed62201_trace.json`
- Analysis: `harness/reports/2026-05-27_rl_curriculum_stage02_staged_opening_stochastic_probe_001/trace_analysis.json`

## Probe

Same staged policy, same `soda-creek` seed `62201`, same `60s` opening handoff. Only action selection changed from deterministic to stochastic.

Two one-episode stochastic probes survived to `180.0095s`. The traced run ended in victory with level `7`, kills `366`, damage taken `25.7433`, normalized action entropy `0.8003`.

## Deterministic vs Stochastic

| Window | Deterministic | Stochastic |
|---|---|---|
| `60s` handoff | pinned at `(-1200.0, -900.0)`, health `92.4698`, action `7` score `0.8927` | near bottom edge at `(-862.2731, -900.0)`, health `113.2499`, sampled action `5` |
| `60-75s` sampled actions | all action `7` | actions `0/3/4/6/7/8` |
| `75s` state | direct contact, health `59.7596`, enemy pressure `0.8671` | not pinned, health `99.8898`, enemy pressure `0.0821` |
| `90s` state | health `24.8195`, low health risk `0.4091` | health `99.8898`, boundary min `57.6392`, low health risk `0.0` |
| terminal | defeat at `115.5319s` | victory at `180.0095s` |

## Conclusion

The recovery actions already exist in the policy distribution, but deterministic argmax suppresses them into a wall-pushing handoff path. This is useful repair evidence for entropy, temperature, action smoothing, or explicit handoff recovery constraints.

This does not change the gate: stochastic one-seed success is not RL policy acceptance, and stage 02 still must pass deterministic or explicitly seeded stochastic multi-map gates before stage 03.
