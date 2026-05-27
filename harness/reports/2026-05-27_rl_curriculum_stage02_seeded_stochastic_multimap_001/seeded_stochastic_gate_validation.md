# Seeded Stochastic Watch Validation

- Decision: `seeded_stochastic_watch_ready`
- Status: `ready`
- Action random seed: `62201`
- Short report: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_multimap_001/comparison_60s_10seed_seeded_stochastic.json`
- Long report: `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_multimap_001/comparison_180s_3seed_seeded_stochastic.json`

## Map Summary

| Report | Map | Win rate | Entropy | Dominant action |
|---|---|---:|---:|---|
| short_report | soda-creek | 1.0 | 0.8332 | 7 @ 0.2971 |
| short_report | caramel-workshop | 1.0 | 0.8187 | 7 @ 0.322 |
| short_report | cracked-star-jar | 1.0 | 0.8413 | 7 @ 0.288 |
| long_report | soda-creek | 1.0 | 0.8359 | 4 @ 0.294 |
| long_report | caramel-workshop | 1.0 | 0.8377 | 4 @ 0.2846 |
| long_report | cracked-star-jar | 1.0 | 0.8065 | 4 @ 0.3189 |

## Limitations

- This is watch evidence only, not RL policy acceptance.
- Deterministic gates and failure-case review still control stage progression.
