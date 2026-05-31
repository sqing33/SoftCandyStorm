# RL Failure Lane Opening Repair Branch Preflight

- Decision: `repair_only_opening_branch_full_regression_failed`
- Lane: `opening_repair`
- Map / seed: `caramel-workshop:63402`
- Base model: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/ppo_opening_mid_boundary_retention_seed63405_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Gate conclusion: `repair`

## Results

| Probe | Target seed result | Preflight | Key action ratios | Branch usage | Notes |
|---|---|---|---|---|---|
| `30-45s` branch | `60.0328s` victory | failed | `5=0.308162`, `7=0.350916` | `1/1801` | action `5` remains just above the `0.300000` cap |
| `30-50s` branch | `60.0328s` victory | failed | `5=0.308162`, `7=0.350916` | `1/1801` | widening the upper bound did not change the online branch intervention |
| `30-55s` branch | `60.0328s` victory | failed | `5=0.308162`, `7=0.350916` | `1/1801` | same target distribution as `30-45s` |
| `30-60s` branch | `60.0328s` victory | failed | `5=0.308162`, `7=0.350916` | `1/1801` | same target distribution as `30-45s` |
| `0-60s` branch | `60.0328s` victory | passed | `5=0.112715`, `7=0.556358` | `1/1801` | useful diagnostic, but it shifts target seed behavior toward action `7` dominance |

The broad `0-60s` branch also passed the `60s/caramel-workshop` window target preflight on the 3-map high-pressure smoke. In that report, `caramel-workshop` reached `0.6667` win rate, `55.9217s` average survival, normalized action entropy `0.4817`, and dominant action ratio `0.6243` for action `7`. Branch usage remained tiny and scoped: `3/5033` decisions on `caramel-workshop`, `0/4723` on `soda-creek`, and `0/5403` on `cracked-star-jar`.

## Full Parent No-Regression Follow-Up

The broad `0-60s` branch failed high-pressure parent no-regression against the unbranched base report.

| Window | Map | Win Delta | Survival Delta | Action L1 Delta | Main Drift | Status |
|---|---|---:|---:|---:|---|---|
| `60s` | `caramel-workshop` | `0.3334` | `6.6443` | `0.2031` | action `7 +0.0768`, action `5 -0.0867` | pass |
| `180s` | `caramel-workshop` | `0.3333` | `46.6366` | `0.4813` | action `5 +0.1270` | regression |
| `300s` | `caramel-workshop` | `0.0` | `60.2395` | `0.5787` | action `5 +0.1940` | regression |

All `soda-creek` and `cracked-star-jar` rows were unchanged because the branch scope was `caramel-workshop` only. The full regression report is `window_regression_high_pressure_window0_60_vs_base.json`, with `2` blockers:

- `180s/caramel-workshop`: action distribution L1 `0.4813 > 0.45`
- `300s/caramel-workshop`: action distribution L1 `0.5787 > 0.45`

## Interpretation

The narrow window is not enough: it fixes terminal outcome for the single target seed but fails the action-ratio target because action `5` remains above the allowed cap.

The broad `0-60s` window is the first positive short-window diagnostic for this lane: it passes both `caramel-workshop:63402` target seed preflight and the `60s/caramel-workshop` hard preflight. However, it is not policy acceptance evidence. The full follow-up shows that the short-window intervention still changes the `caramel-workshop` action distribution too much at `180s` and `300s`, mainly by raising action `5` in longer windows.

## Blockers

- `30-45s`, `30-50s`, `30-55s`, and `30-60s` target seed preflights fail on action `5` ratio `0.308162 > 0.300000`.
- `0-60s` broad branch failed full `60/180/300s` high-pressure parent no-regression with `2` caramel-workshop action-distribution blockers.
- `0-60s` broad branch has not passed `caramel-workshop` seeds `63400-63409` follow-up.
- `0-60s` broad branch increases target-seed action `7` ratio to `0.556358` and `60s/caramel-workshop` dominant action ratio to `0.6243`, so it needs online action-distribution review before any follow-up.

## Next Validation

Do not continue with a shared PPO continuation from this checkpoint and do not run the broad branch as a 10 seed follow-up until its parent-preservation blocker is fixed. The next step should design a narrower state-conditioned dispatch that keeps the `0-60s` action `5` reduction while avoiding broad action `7` dominance and long-window action `5` drift.

Any follow-up still must satisfy the `failure_lane_repair_preflight` contract: target seed preflight, `60s/caramel-workshop` hard preflight, high-pressure `60/180/300s` parent no-regression, and relevant 10 seed caramel follow-up.
