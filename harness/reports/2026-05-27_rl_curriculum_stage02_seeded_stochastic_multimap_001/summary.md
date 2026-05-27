# RL Curriculum Stage 02 Seeded Stochastic Multimap Probe

- Decision: `stage02_seeded_stochastic_multimap_watch_not_gate`
- 60s comparison: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_multimap_001/comparison_60s_10seed_seeded_stochastic.json`
- 180s comparison: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_multimap_001/comparison_180s_3seed_seeded_stochastic.json`
- Watch validation: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_multimap_001/seeded_stochastic_gate_validation.md`

## Probe

Same staged policy as the deterministic stage 02 handoff regression:

- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_001/stage02_opening_edge_delta.zip`
- Action selection: `stochastic`
- Action random seed: `62201`
- Map preset: `high-pressure`

## Results

| Window | Seeds | soda-creek | caramel-workshop | cracked-star-jar |
|---|---:|---:|---:|---:|
| `60s` opening gate probe | 10 | 100%, entropy `0.8332` | 100%, entropy `0.8187` | 100%, entropy `0.8413` |
| `180s` handoff probe | 3 | 100%, entropy `0.8359` | 100%, entropy `0.8377` | 100%, entropy `0.8065` |

Both reports keep `gate_decision = multimap_comparison_recorded_not_balance_gate`; that means the comparison recorded no action-distribution repair finding, not that the policy is accepted.

`tools/validate_seeded_stochastic_gate.py` returns `seeded_stochastic_watch_ready` for this pair: same action seed, stochastic action selection, high-pressure three-map preset, 60s / 10 seed coverage, 180s / 3 seed coverage, 100% policy win rate, and entropy above the watch threshold. The validator intentionally cannot output RL acceptance.

## Conclusion

The seeded stochastic path is now a stronger repair direction than the earlier unseeded one-seed probe: with the same action sampling seed, it clears the current 60s opening regression window and the 180s three-map handoff smoke. It still does not promote stage 02. The deterministic policy remains blocked by the `soda-creek` handoff failure, and seeded stochastic evaluation needs an explicit multi-seed gate definition before it can affect stage progression or RL policy acceptance.
