# RL Curriculum Stage 02 Seeded Stochastic Probe

- Decision: `stage02_seeded_stochastic_probe_recorded_not_gate`
- Repro run 1: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_probe_001/evaluation_seed62201_run1.json`
- Repro run 2: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_probe_001/evaluation_seed62201_run2.json`
- Trace evaluation: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_probe_001/evaluation_seed62201_trace.json`
- Trace: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_probe_001/traces/soda-creek_seed62201_trace.json`
- Analysis: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_probe_001/trace_analysis.json`

## Probe

Same staged policy, same `soda-creek` map seed `62201`, same `60s` opening handoff. Action selection is stochastic with explicit `action_random_seed = 62201`.

The two no-trace seeded stochastic runs are byte-identical (`8ba7283e0576...`), and the traced run has the same summary and action counts. The policy survives to `180.0095s` with win rate `1.0`, kills `385`, damage taken `7.9700`, and normalized action entropy `0.8275`.

## Handoff Readout

| Window | Seeded stochastic result |
|---|---|
| `60s` handoff | position `(497.8561, 133.6539)`, health `119.55`, action `2`, chosen score `0.7081` |
| `60-75s` sampled actions | `0, 1, 2, 3, 4, 5, 6, 7, 8` |
| `75s` state | position `(316.7212, -343.1545)`, health `119.55`, enemy pressure `0.0` |
| `90s` state | boundary min `150.4059`, enemy pressure `0.0`, low-health risk `0.0` |
| terminal | victory at `180.0095s`, health `112.0299` |

## Conclusion

This converts the earlier stochastic probe from "lucky unseeded run" into reproducible diagnostic evidence. It still does not change the gate: deterministic stage 02 remains blocked by the `soda-creek` handoff regression, and seeded stochastic success on one seed is not RL policy acceptance or stage 03 permission.
