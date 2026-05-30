# Policy Trace Samples Export

- Decision: `policy_trace_samples_exported`
- Samples: `387`
- Output: `harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_defeat_terminal_210_300_policy_rows.jsonl`

## Action Distribution

| Action | Count | Ratio |
|---|---:|---:|
| `1` | `60` | `0.155` |
| `2` | `16` | `0.0413` |
| `3` | `84` | `0.2171` |
| `4` | `13` | `0.0336` |
| `5` | `80` | `0.2067` |
| `6` | `3` | `0.0078` |
| `7` | `49` | `0.1266` |
| `8` | `82` | `0.2119` |

## Trace Summaries

| Trace | Seed | Kept |
|---|---:|---:|
| `harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/traces/caramel-workshop_seed63400_trace.json` | `63400` | `21` |
| `harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/traces/caramel-workshop_seed63401_trace.json` | `63401` | `153` |
| `harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/traces/caramel-workshop_seed63402_trace.json` | `63402` | `213` |

## Dropped Counts

- `time_before_min`: `3780`

## Limitations

- Exported samples come from sampled policy traces, not full replays.
- The output is supervised retention or repair input only, not policy acceptance evidence.
- Any model trained from these samples must still pass target-seed preflight, fixed-window high-pressure comparison, no-regression, and failure-case review.
