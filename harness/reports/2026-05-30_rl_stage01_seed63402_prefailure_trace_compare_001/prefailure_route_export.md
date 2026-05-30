# Policy Trace Samples Export

- Decision: `policy_trace_samples_exported`
- Samples: `48`
- Output: `harness/reports/2026-05-30_rl_stage01_seed63402_prefailure_trace_compare_001/seed63402_prefailure_route_states.jsonl`

## Action Distribution

| Action | Count | Ratio |
|---|---:|---:|
| `5` | `48` | `1.0` |

## Trace Summaries

| Trace | Seed | Kept |
|---|---:|---:|
| `harness/reports/2026-05-30_rl_stage01_seed63402_prefailure_trace_compare_001/guard_retention_probe_traces/soda-creek_seed63402_trace.json` | `63402` | `16` |
| `harness/reports/2026-05-30_rl_stage01_seed63402_trace_diagnostic_001/candidate_traces/soda-creek_seed63402_trace.json` | `63402` | `16` |
| `harness/reports/2026-05-30_rl_stage01_seed63402_trace_diagnostic_001/parent_traces/soda-creek_seed63402_trace.json` | `63402` | `16` |

## Dropped Counts

- `boundary_edge_below_min`: `78`
- `enemy_pressure_below_min`: `211`
- `max_samples_per_trace`: `3`
- `seed_filtered_trace`: `6`

## Limitations

- Exported samples come from sampled policy traces, not full replays.
- The output is supervised retention or repair input only, not policy acceptance evidence.
- Any model trained from these samples must still pass target-seed preflight, fixed-window high-pressure comparison, no-regression, and failure-case review.
