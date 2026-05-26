# RL Rule Bot Phase-Aligned Trajectory Export

- Bot: `kite`
- Map preset: `high-pressure`
- Maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- Seeds: `48000` to `48009`
- Duration: `300` seconds
- Sample stride: `10`
- Observation version: `2`
- Content hash: `fnv1a64:4ad1c52ac3f1285b`
- Gate decision: `trajectory_export_recorded_not_policy_gate`

## Exported Samples

| Map | Samples | Skipped upgrade samples | Victories |
|---|---:|---:|---:|
| `soda-creek` | 7145 | 93 | 6 |
| `caramel-workshop` | 6778 | 82 | 2 |
| `cracked-star-jar` | 7803 | 101 | 5 |

## Phase Filter Dry-Run

| Phase | Samples | Time range | Notes |
|---|---:|---|---|
| `opening` | 5388 | `0.0` - `59.9994` | Phase-aligned with the staged policy 0.2 threshold in a 300 second episode. |
| `mid` | 9911 | `60.3328` - `179.6761` | Covers the middle pressure window. |
| `late` | 6427 | `180.0095` - `299.6817` | Covers late low-health and Boss pressure states. |

## Findings

- This export fixes the earlier staged training mismatch where 60 second trajectories made `opening` cover only roughly the first 12 seconds.
- The opening dry-run still reported `high_action_persistence`, so this data is a repair attempt, not policy evidence.
- These trajectories are supervised movement samples only and do not include upgrade-choice targets.
