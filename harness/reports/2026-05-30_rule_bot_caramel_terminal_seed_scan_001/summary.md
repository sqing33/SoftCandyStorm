# Rule Bot Caramel Terminal Seed Scan

- item_id: `rule_bot_caramel_terminal_seed_scan`
- gate_decision: `rule_bot_terminal_seed_scan_recorded_not_policy_gate`
- scope: `caramel-workshop`, seeds `63400-63402` target scan plus `63380-63420` neighbor scan, `300s`
- baseline context: current per-map edge branch + all-map late filter still needs a `caramel-workshop` late conversion target

## Target Seed Result

The exact failing target seeds `63400-63402` were scanned with all 9 rule bots at `300s`. No rule bot converted any of the target seeds into a victory.

| Bot | Victories | Average survival |
|---|---:|---:|
| `idle` | `0/3` | `116.3s` |
| `random` | `0/3` | `222.1s` |
| `coward` | `0/3` | `199.1s` |
| `greedy` | `0/3` | `191.2s` |
| `kite` | `0/3` | `222.1s` |
| `tank` | `0/3` | `224.7s` |
| `boss-hunter` | `0/3` | `215.2s` |
| `zone-control` | `0/3` | `225.0s` |
| `route` | `0/3` | `149.9s` |

## Neighbor Seed Result

The wider neighbor scan over seeds `63380-63420` found `16` victory episodes across 6 rule bots. This gives much closer same-map success coverage than the older multimap victory terminal dataset, whose usable `caramel-workshop` rows came only from seed `62301`.

| Bot | Victories | Win rate |
|---|---:|---:|
| `random` | `2/41` | `0.049` |
| `greedy` | `2/41` | `0.049` |
| `kite` | `9/41` | `0.220` |
| `boss-hunter` | `1/41` | `0.024` |
| `zone-control` | `1/41` | `0.024` |
| `route` | `1/41` | `0.024` |

Closest useful victories include `boss-hunter@63399`, `greedy@63395`, `kite@63395`, `kite@63406`, `route@63412`, `kite@63414`, `zone-control@63415`, `random@63417`, `greedy@63417`, and `kite@63418`.

## Filtered Victory Samples

The successful neighbor trajectories were exported with observation v2 and filtered to victory episodes in the `210-300s` terminal window.

| Output | Decision | Count | Notes |
|---|---|---:|---|
| `caramel_rule_bot_victory_210_300_samples.jsonl` | `bot_trajectory_samples_filtered` | `8630` samples / `16` episodes | Same-map `caramel-workshop` victory movement samples only. |
| `behavior_clone_dry_run_rule_victory.json` | `dataset_validated_not_training_gate` | `8630` samples / `16` episodes | Loader check passes with observation_len `145`, action_count `9`, late_low_health ratio `0.9532`, no diagnosis flags. |
| `nearest_rule_victory_seed63400.json` | `trace_dataset_nearest_neighbor_recorded_watch_only` | `1281` trace samples | nearest match ratio `0.5527`, average distance `2.528792`. |
| `nearest_rule_victory_seed63401.json` | `trace_dataset_nearest_neighbor_recorded_watch_only` | `1413` trace samples | nearest match ratio `0.5605`, average distance `2.416173`. |
| `nearest_rule_victory_seed63402.json` | `trace_dataset_nearest_neighbor_recorded_watch_only` | `1473` trace samples | nearest match ratio `0.4182`, average distance `2.45622`. |

Compared with the older same-map victory target check (`0.0`, `0.1569`, `0.169` match ratios against seed `62301`-only candidates), the new rule-bot neighbor dataset is a materially better coverage source for the current failure surface. It is still only diagnostic / training input evidence.

## Conclusion

The target seeds themselves appear hard enough that existing rule bots do not produce direct successes, but nearby seeds provide `16` same-map terminal victory episodes and `8630` usable `210-300s` observation/action samples. The next repair step should train or dry-run a new `caramel-workshop` terminal branch from these neighbor victory samples, while mixing the current `164` clean risk rows only as low-weight safety repair input and preserving the per-map edge branch + all-map late filter baseline.

This report does not approve an RL checkpoint, policy candidate, stage 03 model, balance gate, or release evidence.
