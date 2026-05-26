# RL Behavior Clone Map Conditioning Dry Run

- Decision: `dataset_validated_not_training_gate`
- Dataset samples: `5312`
- Episodes: `15`
- Observation len: `145`
- Action count: `9`
- Maps: `caramel-workshop`, `cracked-star-jar`, `soda-creek`

## Dataset Shape

| Map | Samples | Ratio |
|---|---:|---:|
| `caramel-workshop` | 1708 | 0.3215 |
| `cracked-star-jar` | 1801 | 0.3390 |
| `soda-creek` | 1803 | 0.3394 |

## Notes

- This dry run proves the input datasets carry usable `map_id` metadata for one-hot conditioning.
- It is not training evidence, policy evidence, balance evidence, or fun evidence.

