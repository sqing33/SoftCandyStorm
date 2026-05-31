# Rule Bot Caramel Wide Terminal Seed Scan

- item_id: `rule_bot_caramel_wide_terminal_seed_scan`
- gate_decision: `rule_bot_wide_terminal_seed_scan_recorded_not_training_gate`
- scope: `caramel-workshop`, seeds `63300-63500`, 6 rule bots, `300s`
- baseline context: the rejected `caramel-workshop` terminal branch showed that closer same-map victory samples alone did not convert seeds `63400-63402`

## Matrix Result

The previous target scan already showed that all 9 rule bots fail directly on seeds `63400-63402`. This wider scan reran the 6 rule bots that had produced neighbor victories, over a `201` seed window. The target seeds still had no direct victory in this wider matrix.

| Bot | Victories | Win rate | Closest useful victories |
|---|---:|---:|---|
| `random` | `4/201` | `0.020` | `63393`, `63417` |
| `greedy` | `11/201` | `0.055` | `63395`, `63417` |
| `kite` | `48/201` | `0.239` | `63390`, `63391`, `63392`, `63395`, `63397`, `63406`, `63414`, `63418` |
| `boss-hunter` | `12/201` | `0.060` | `63399` |
| `zone-control` | `5/201` | `0.025` | `63415` |
| `route` | `5/201` | `0.025` | `63412` |

The closest useful success remains `boss-hunter@63399`, one seed away from target seed `63400`. The wider scan found more total victories, but did not find a same-seed target success or a closer success than the existing neighbor scan.

## Filtered Victory Samples

The six bot trajectory exports were filtered to `caramel-workshop`, `victory`, `210-300s` movement samples:

| Output | Decision | Count | Notes |
|---|---|---:|---|
| `/private/tmp/soft-candy-caramel-wide-trajectories-63300-63500/caramel_rule_bot_wide_victory_210_300_samples.jsonl` | `bot_trajectory_samples_filtered` | `45853` samples / `85` episodes | Temporary diagnostic input, not committed because it is about `61M` and not yet accepted as a durable training source. |
| `wide_victory_sample_filter.json` | `bot_trajectory_samples_filtered` | `107661` source samples / `1206` source episodes | Compact committed filter report. |

## Nearest Coverage

Compared with the prior `8630`-sample neighbor dataset:

| Trace | Old candidates | Old match | Old avg distance | Wide candidates | Wide match | Wide avg distance |
|---|---:|---:|---:|---:|---:|---:|
| `seed63400` | `8630` | `0.5527` | `2.528792` | `45853` | `0.4176` | `2.401258` |
| `seed63401` | `8630` | `0.5605` | `2.416173` | `45853` | `0.5534` | `2.252513` |
| `seed63402` | `8630` | `0.4182` | `2.456220` | `45853` | `0.4915` | `2.319987` |

The wider dataset reduces nearest-neighbor distance for all three failing traces, which means it contains closer observation states. However, the nearest target action agreement regresses on `seed63400`, is effectively flat on `seed63401`, and only improves on `seed63402`.

## Episode Ranking

`python/train/rank_behavior_clone_dataset_episodes.py` ranks victory episodes by how often their samples become nearest neighbors of the three failing traces and whether those nearest samples match the online action.

The combined top episodes are:

| Rank | Episode | Top1 hits | Match ratio | Avg distance |
|---:|---|---:|---:|---:|
| `1` | `greedy@63463` | `513` | `0.6335` | `2.430600` |
| `2` | `greedy@63417` | `238` | `0.8403` | `2.306473` |
| `3` | `greedy@63489` | `169` | `0.8521` | `2.423738` |
| `4` | `greedy@63488` | `148` | `0.8649` | `2.485289` |
| `5` | `route@63333` | `139` | `0.9209` | `2.209728` |

The ranking suggests that a selective weighting experiment should start from high-match episodes such as `greedy@63417`, `greedy@63489`, `greedy@63488`, `route@63333`, `route@63412`, or `route@63348`, rather than blindly using all `45853` wide samples. `greedy@63463` has the most hits, but its match ratio is only `0.6335`, so it should be treated as a coverage-heavy but risky source.

## Conclusion

This is mixed diagnostic evidence, not a training gate. The wider scan is useful for understanding the failure surface, but it does not justify another plain supervised terminal-path imitation branch by itself.

Next repair should shift toward a constrained online / sequence objective, or a more selective trajectory weighting strategy that preserves the current per-map edge branch plus all-map late filter no-regression baseline. The rejected `ppo_caramel_rule_victory_terminal_branch.zip` remains rejected and must not be promoted as a policy candidate, stage 03 model, RL test Bot, balance gate, or release evidence.
