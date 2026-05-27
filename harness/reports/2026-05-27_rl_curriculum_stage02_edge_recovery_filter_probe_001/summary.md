# RL Curriculum Stage 02 Edge Recovery Filter Probe

- Decision: `stage02_edge_recovery_filter_watch_not_gate`
- Single-seed trace evaluation: `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_filter_probe_001/evaluation_seed62201_trace.json`
- Trace: `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_filter_probe_001/traces/soda-creek_seed62201_trace.json`
- 60s comparison: `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_filter_probe_001/comparison_60s_10seed.json`
- 180s comparison: `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_filter_probe_001/comparison_180s_3seed.json`

## Probe

Same staged policy as the deterministic handoff failure, evaluated with deterministic actions plus `policy_adapter.mode = edge_recovery_filter`. The adapter only changes an action when the player is within `32` units of a map edge and the selected action keeps pushing farther into that edge.

## Results

| Window | Seeds | soda-creek | caramel-workshop | cracked-star-jar |
|---|---:|---:|---:|---:|
| `60s` opening gate probe | 10 | 100%, entropy `0.6500` | 100%, entropy `0.7215` | 100%, entropy `0.6011` |
| `180s` handoff probe | 3 | 100%, entropy `0.6236` | 100%, entropy `0.6787` | 100%, entropy `0.5591` |

The failed deterministic reference seed `soda-creek / 62201` now survives to `180.0095s` with level `8`, kills `365`, damage taken `58.2601`, and normalized action entropy `0.6127`. At the 60s handoff it is no longer pinned at `(-1200, -900)`; the trace sample is around `(-1046.7123, -699.7333)` with health `119.25`.

## Conclusion

This strongly supports the diagnosis that the stage 02 failure is a deterministic edge-pushing handoff bug, not a lack of recovery actions in the policy distribution. It still cannot promote the policy: `edge_recovery_filter` is a hand-written diagnostic adapter, and `tools/validate_rl_policy_acceptance.py` rejects reports that include `policy_adapter`.
