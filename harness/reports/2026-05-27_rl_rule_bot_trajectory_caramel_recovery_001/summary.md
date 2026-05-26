# RL Rule Bot Trajectory Caramel Recovery

- Bot: `kite`
- Map: `caramel-workshop`
- Seeds: `46000` to `46004`
- Duration: `300` seconds
- Sample start: `180` seconds
- Sample stride: `5`
- Output: `harness/reports/2026-05-27_rl_rule_bot_trajectory_caramel_recovery_001/kite_caramel_workshop.jsonl`

## Result

| Metric | Value |
|---|---:|
| Samples | 2041 |
| Episodes | 5 |
| Victories | 1 |
| Skipped upgrade samples | 11 |

## Limitations

- This trajectory export is a focused recovery-data source, not a policy gate.
- A policy trained with this data must still pass multi-map 60/300 second comparisons before promotion.
