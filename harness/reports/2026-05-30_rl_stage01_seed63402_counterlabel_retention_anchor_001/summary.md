# Stage 01 Seed 63402 Counterlabel + Retention Anchor

- Decision: `anchor_trained_not_policy_gate`
- Model: `seed63402_counterlabel_retention_anchor.pt`
- Counterlabel rows: `harness/reports/2026-05-30_rl_stage01_seed63402_counterlabel_prefailure_states_001/seed63402_prefailure_counterlabel_samples.jsonl`
- Success retention rows: `harness/reports/2026-05-30_rl_stage01_seed63402_success_retention_samples_001/soda_success_opening_retention_samples.jsonl`

## Results

| Check | Result |
|---|---|
| Total samples | `80` |
| Counterlabel rows | `48` pre-failure repair hypothesis rows |
| Retention rows | `32` successful parent trace rows |
| Map / window | `soda-creek`, `31.9999s-37.3331s` |
| Action distribution | action `7` = `56/80`, action `3` = `24/80` |
| Observation shape | `observation_len = 145`, `action_count = 9` |
| Train accuracy | `0.7344` |
| Validation accuracy | `0.8125` |
| Offline diagnostic | `watch_only`, accuracy `0.75`, predicted action `7` = `52/80`, action `3` = `28/80` |
| Gate decision | `behavior_clone_smoke_only_not_policy_gate` |

## Conclusion

The anchor removed the observed failure action `5` from the local repair target and learned a mixed action `7` / `3` objective, but it did not form a high-confidence offline target. It is usable only as a small repair hypothesis for the immediately following PPO probe.

It is not a policy gate, not observed successful behavior, and not evidence that seed `63402` is repaired.

## Validation

- `behavior_clone_anchor_report.json`: `status = trained`, `behavior_clone_smoke_only_not_policy_gate`.
- `offline_policy_diagnostic.json`: `offline_policy_diagnostic_recorded_watch_only`, overall accuracy `0.75`.
- Paired probe report: `harness/reports/2026-05-30_rl_stage01_seed63402_counterlabel_retention_probe_001/summary.md`.
