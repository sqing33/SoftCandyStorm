# Caramel Late Conversion Diagnostic

- Decision: `caramel_late_conversion_diagnostic_recorded_needs_split_repair`
- Source comparison: `harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_comparison_300s.json`
- Scope: `caramel-workshop`, seeds `63400-63402`, `300s`
- Policy stack: e30 mid-anchor parent + `edge_recovery_branch` + `late_recovery_filter`

## Result

The single-map trace replay reproduced the chained comparison result: `caramel-workshop` stayed at `0.0` win rate with average survival `163.3014s`. The wrapped `edge_recovery_branch` made `0` dispatches on this map because it is intentionally scoped to `soda-creek`.

Failure analysis shows mixed failure modes, not one pure late-conversion gap:

| Seed | Result | Time | Bucket | Main observation |
|---:|---|---:|---|---|
| `63400` | defeat | `213.2166s` | `late_180_to_300` | Low health + hazard pressure near the right edge; final top action remains `5`. |
| `63401` | defeat | `235.3546s` | `late_180_to_300` | Low health + hazard pressure away from hard edge; final top action is `2`. |
| `63402` | defeat | `41.333s` | `opening_lt_60` | Early bottom-right corner lock; action `5` is `60.47%`, action `7` never appears. |

## Clean Sample Split

Risk sample filtering produced a clean repair-input subset:

| Slice | Input | Kept | Dropped | Validation |
|---|---:|---:|---:|---|
| `60-180s` | `162` | `158` | `4` | `risk_recovery_samples_valid` |
| `180-300s` | `264` | `100` | `164` | `risk_recovery_samples_valid` |
| Combined | `258` | `258` | `0` | `risk_recovery_samples_valid`, `0` warnings |

The combined clean subset has `139` `wallward_edge`, `70` `toward_enemy_pressure`, `49` `toward_hazard`, and `3` `toward_boss` risk reasons. Every retained target has no residual target risk reasons under the validator.

## Trace Hotspots

`analyze_route_recovery_traces.py` inspected `495` sampled trace rows and found `147` negative `route_recovery` rows (`29.70%`). The hotspots are concentrated before the late window:

| Bucket | Hotspots | Min route recovery | Avg route recovery |
|---|---:|---:|---:|
| `opening_lt_60` | `100` | `-0.0125` | `-0.0068` |
| `mid_60_to_180` | `32` | `-0.0022` | `-0.0008` |
| `late_180_to_300` | `15` | `-0.0021` | `-0.0008` |

The strongest pressure tag is `boundary_edge` with `111` hotspots. This supports splitting the repair target: seed `63402` needs an opening / edge escape fix, while seeds `63400` and `63401` need late hazard + low-health conversion support.

## Conclusion

The chained wrapper provides useful repair evidence, but the remaining `caramel-workshop` problem is not solved by one broader late filter. The next repair should be split:

- `caramel opening`: target seed `63402` bottom-right edge lock before `60s`.
- `caramel late`: use the `100` clean `180-300s` risk rows as low-weight repair input, then validate against the existing 60 / 180 / 300 second no-regression windows.
- `caramel conversion`: collect or compare successful `caramel-workshop` long-window trajectories before training a terminal branch, because clean risk rows only say which actions are safer, not how to finish the run.

This report is diagnostic evidence only and does not approve a policy candidate.
