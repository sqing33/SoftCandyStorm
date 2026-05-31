# Caramel Selective Terminal Branch Sequence Diagnostic

- Decision: `terminal_sequence_diagnostic_recorded_watch_only`
- Scope: `caramel-workshop` 300s failed-only traces for the w0.5 selective ranked terminal branch
- Baseline chain: per-map edge branch + all-map late recovery filter
- Terminal model: `harness/reports/2026-05-31_rl_caramel_selective_ranked_victory_terminal_branch_w05_001/ppo_caramel_selective_ranked_victory_terminal_branch_w05.zip`
- Offline target dataset: `harness/reports/2026-05-31_rule_bot_caramel_wide_terminal_seed_scan_001/caramel_selective_ranked_victory_210_300_samples.jsonl`

## Result

The trace replay reproduced the same online failure shape as the 300s comparison:

| Seed | Terminal time | Terminal | Trace samples | Nearest match | Avg distance |
|---:|---:|---|---:|---:|---:|
| `63400` | `213.2166s` | `defeat` | `1281` | `0.8509` | `2.550705` |
| `63401` | `235.2880s` | `defeat` | `1413` | `0.8634` | `2.425201` |
| `63402` | `244.0898s` | `defeat` | `1466` | `0.8172` | `2.490466` |

The terminal branch was active on the target map: `832 / 20776` decisions overall and `832 / 4576` decisions in `late_180_to_300`. Despite that, all three target seeds still ended in `player_health_depleted`.

## Late Window

| Seed | Window | Samples | Online top | Nearest target top | Match ratio | Avg distance |
|---:|---|---:|---|---|---:|---:|
| `63400` | `180-210s` | `180` | `3` / `0.4167` | `3` / `0.4111` | `0.8500` | `2.281342` |
| `63400` | `210-240s` | `21` | `5` / `1.0000` | `5` / `0.9048` | `0.9048` | `2.944834` |
| `63401` | `180-210s` | `180` | `5` / `0.3000` | `5` / `0.3222` | `0.8611` | `1.994330` |
| `63401` | `210-240s` | `153` | `7` / `0.2941` | `1` / `0.2026` | `0.8105` | `2.492119` |
| `63402` | `180-210s` | `180` | `8` / `0.2833` | `7` / `0.2722` | `0.9278` | `2.301766` |
| `63402` | `210-240s` | `180` | `1` / `0.3500` | `1` / `0.2333` | `0.7111` | `2.655651` |
| `63402` | `240-270s` | `26` | `5` / `1.0000` | `5` / `0.9231` | `0.9231` | `2.584260` |

## Interpretation

The selective victory target is not failing because the branch is unused or because nearest action agreement is low. The target actions remain fairly close to the online sequence, including the final sampled windows, but the online closed loop still runs into lethal low-health / hazard pressure. This reinforces the gate conclusion: simple supervised terminal-path imitation is exhausted for this failure face.

Next follow-up should change the objective, not just the dataset weight. Good candidates are direct target-seed successful trajectories, a constrained online terminal objective, or a sequence-level objective that rewards health / hazard recovery across the whole `210-300s` rollout before any new terminal branch is eligible for the terminal conversion probe gate.

## Artifacts

- `comparison_300s_caramel_trace.json`
- `traces/caramel-workshop_seed63400_trace.json`
- `traces/caramel-workshop_seed63401_trace.json`
- `traces/caramel-workshop_seed63402_trace.json`
- `nearest_selective_ranked_online_seed63400.json`
- `nearest_selective_ranked_online_seed63401.json`
- `nearest_selective_ranked_online_seed63402.json`
- Matching Markdown summaries for the nearest-neighbor reports

## Limitations

- This is diagnostic evidence only, not a policy gate or RL acceptance report.
- It samples policy traces every `5` policy steps, not every GameCore tick.
- Nearest-neighbor agreement does not prove that imitating those actions produces a stable online rollout.
