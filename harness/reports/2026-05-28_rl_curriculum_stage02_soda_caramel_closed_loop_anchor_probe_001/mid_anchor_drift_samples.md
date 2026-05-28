# Anchor Drift Samples

- Decision: `anchor_drift_samples_recorded`
- Inspected samples: `36426`
- Matched samples: `2888`
- Exported samples: `200`
- Time bucket filter: `['mid_60_to_180']`
- Map filter: `['all']`
- Minimum KL: `0.35`
- Only disagreement: `True`

## Summary

| Scope | Samples | Mean KL | Max KL | Disagreement |
| --- | ---: | ---: | ---: | ---: |
| `overall` | `200` | `2.228259` | `3.513148` | `1.0` |

## By Map

| Map | Samples | Mean KL | Max KL | Disagreement |
| --- | ---: | ---: | ---: | ---: |
| `caramel-workshop` | `32` | `2.286731` | `3.498356` | `1.0` |
| `cracked-star-jar` | `128` | `2.275991` | `2.994162` | `1.0` |
| `soda-creek` | `40` | `2.028737` | `3.513148` | `1.0` |

## By Time Bucket

| Bucket | Samples | Mean KL | Max KL | Disagreement |
| --- | ---: | ---: | ---: | ---: |
| `mid_60_to_180` | `200` | `2.228259` | `3.513148` | `1.0` |

## Top Examples

| Map | Seed | Time | KL | Anchor | Candidate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `soda-creek` | `63101` | `69.3993` | `3.513148` | `4` | `8` |
| `caramel-workshop` | `63102` | `91.3323` | `3.498356` | `8` | `4` |
| `soda-creek` | `63101` | `67.9993` | `3.039523` | `4` | `8` |
| `cracked-star-jar` | `63101` | `120.3318` | `2.994162` | `8` | `4` |
| `cracked-star-jar` | `63102` | `89.6656` | `2.939533` | `8` | `4` |
| `cracked-star-jar` | `63102` | `89.3323` | `2.866287` | `8` | `4` |
| `cracked-star-jar` | `63101` | `118.9985` | `2.860322` | `8` | `4` |
| `cracked-star-jar` | `63101` | `119.3319` | `2.848896` | `8` | `4` |
| `cracked-star-jar` | `63102` | `91.3323` | `2.838845` | `8` | `4` |
| `caramel-workshop` | `63102` | `92.6656` | `2.823524` | `8` | `4` |

## Limitations

- This report is offline anchor-drift diagnostic evidence only.
- Exported rows are not RL policy acceptance evidence.
- Any repair trained from these rows must rerun deterministic high-pressure, no-regression, and repair-probe gates.
