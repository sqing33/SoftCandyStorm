# Policy Trace Samples Export

- Decision: `policy_trace_samples_exported`
- Samples: `32`
- Output: `harness/reports/2026-05-30_rl_stage01_seed63402_success_retention_samples_001/soda_success_opening_retention_samples.jsonl`

## Action Distribution

| Action | Count | Ratio |
|---|---:|---:|
| `7` | `32` | `1.0` |

## Trace Summaries

| Trace | Seed | Kept |
|---|---:|---:|
| `harness/reports/2026-05-30_rl_stage01_seed63402_trace_diagnostic_001/parent_traces/soda-creek_seed63400_trace.json` | `63400` | `16` |
| `harness/reports/2026-05-30_rl_stage01_seed63402_trace_diagnostic_001/parent_traces/soda-creek_seed63401_trace.json` | `63401` | `16` |

## Dropped Counts

- `seed_filtered_trace`: `1`
- `time_after_max`: `140`
- `time_before_min`: `192`

## Limitations

- Exported samples come from sampled policy traces, not full replays.
- The output is supervised retention or repair input only, not policy acceptance evidence.
- Any model trained from these samples must still pass target-seed preflight, fixed-window high-pressure comparison, no-regression, and failure-case review.
