# Caramel Late Conversion Target Trace Pack

- item_id: `rl_caramel_late_conversion_target`
- gate_decision: `conversion_target_trace_pack_recorded_not_policy_gate`
- scope: `caramel-workshop`, seeds `63400-63402`, `300s`
- baseline: per-map edge branch (`soda-creek 0-60s`, `caramel-workshop 30-45s`) + all-map `late_recovery_filter`

## Result

This pack reruns the current per-map chain baseline only on `caramel-workshop` with failed-only sampled traces and observation vectors enabled. It reproduces the remaining conversion gap under the latest baseline:

| Seed | Terminal | Time | Notes |
|---:|---|---:|---|
| `63400` | `defeat` | `213.2166s` | Enters the terminal window with very low health; sampled `210-300s` actions are all action `5`. |
| `63401` | `defeat` | `235.3546s` | Dies in late window after mixed movement; dominant sampled online action in `210-300s` is action `7`. |
| `63402` | `defeat` | `243.7898s` | Survives past the previous opening lock but still dies in late window; dominant sampled online action is action `8`. |

The run emitted `374` mixed recovery rows. The raw file intentionally keeps the single edge-branch row for provenance, while the clean late subset filters to `180-300s` risk recovery rows only.

## Exported Inputs

| Output | Decision | Count | Notes |
|---|---|---:|---|
| `caramel_per_map_chain_clean_risk_samples.jsonl` | `risk_recovery_samples_valid` | `164` | Clean `180-300s` risk rows; target risk reasons are all `<none>`. |
| `caramel_defeat_terminal_210_300_policy_rows.jsonl` | `policy_trace_samples_exported` | `387` | Sampled failure-state policy rows from `210-300s`; these are state coverage and observed failed actions, not hard success targets. |
| `behavior_clone_dry_run_clean_risk.json` | `dataset_validated_not_training_gate` | `164` | Confirms the clean risk subset is readable with `risk_recovery_sample_weight=0.5` and `top_k_scores` soft recovery targets. |

## Victory Target Coverage Check

Nearest-neighbor inspection against the existing multimap victory terminal dataset, restricted to same-map `caramel-workshop` rows from `210-240s`, found only `180` offline candidates and all nearest sequences came from seed `62301`.

| Seed | Failure rows | Nearest match ratio | Avg nearest distance | Main mismatch |
|---:|---:|---:|---:|---|
| `63400` | `21` | `0.0` | `4.54615` | Online action `5` does not match nearest victory actions (`1/2/4/8`). |
| `63401` | `153` | `0.1569` | `3.389727` | Nearest victory targets skew action `1/2`, while online trace is more mixed and action `7` heavy. |
| `63402` | `213` | `0.169` | `3.694926` | Nearest victory targets skew action `1`, while online trace is action `8/3/5` heavy. |

## Conclusion

The old multimap victory terminal dataset is too thin for this specific caramel late failure surface: for the latest failing seeds, same-map nearest targets are effectively a single older victory path and do not match most observed failure-state actions. The next training step should not promote these rows directly; it should use the clean `180-300s` risk subset as low-weight safety repair input and collect or synthesize additional successful `caramel-workshop` terminal trajectories closer to seeds `63400-63402` before training another terminal branch.

This report is diagnostic evidence only. It does not approve a policy candidate, stage 03 checkpoint, RL acceptance, balance gate, or release evidence.
