# Six Map Boss Matrix Scoping Summary

- Date: `2026-05-26`
- Content dir: `content/base_demo`
- Seeds: `12345`..`12347` per bot
- Duration target: `600` seconds
- Bots: `kite`, `boss-hunter`, `tank`
- Purpose: scope map-level balance after the caramel-workshop repair.

This is a lightweight scoping report. The raw non-caramel calibration reports were generated under `/tmp/softcandy_six_map_matrix`; the committed caramel-workshop report remains the formal replay-backed gate for the repaired map.

## Results

| Map | Kite | BossHunter | Tank | Gate Read |
|---|---:|---:|---:|---|
| frosting-grassland | 100.0% repair | 100.0% repair | 100.0% repair | broadly too easy |
| soda-creek | 100.0% repair | 100.0% repair | 0.0% repair | split: high-skill too easy, Tank too hard |
| cotton-cloud-pasture | 66.7% pass | 100.0% repair | 100.0% repair | BossHunter/Tank too easy |
| caramel-workshop | 66.7% pass | 66.7% pass | 33.3% pass | repaired in focused gate |
| jelly-platform | 66.7% pass | 100.0% repair | 100.0% repair | BossHunter/Tank too easy |
| cracked-star-jar | 100.0% repair | 100.0% repair | 100.0% repair | broadly too easy |

## Key Findings

- The caramel-workshop repair did not generalize to the full map roster, which is expected because it introduced caramel-specific hazard pressure.
- Maps without equivalent damaging Boss or terrain pressure are still too easy for high-skill and defensive policies.
- soda-creek is asymmetric: Kite and BossHunter overperform, while Tank dies in all three seeds, including two early defeats.
- cotton-cloud-pasture and jelly-platform have at least one high-skill pass case, but BossHunter and Tank still show too little incoming damage.
- cracked-star-jar currently does not behave like a final-map pressure test; all three scoped bots win 3/3.

## Recreate Commands

```bash
cargo run -p game_harness -- matrix --content-dir content/base_demo --map-id frosting-grassland --seconds 600 --seed-start 12345 --seeds 3 --bots kite,boss-hunter,tank --report-dir /tmp/softcandy_six_map_matrix/frosting-grassland
cargo run -p game_harness -- matrix --content-dir content/base_demo --map-id soda-creek --seconds 600 --seed-start 12345 --seeds 3 --bots kite,boss-hunter,tank --report-dir /tmp/softcandy_six_map_matrix/soda-creek
cargo run -p game_harness -- matrix --content-dir content/base_demo --map-id cotton-cloud-pasture --seconds 600 --seed-start 12345 --seeds 3 --bots kite,boss-hunter,tank --report-dir /tmp/softcandy_six_map_matrix/cotton-cloud-pasture
cargo run -p game_harness -- matrix --content-dir content/base_demo --map-id jelly-platform --seconds 600 --seed-start 12345 --seeds 3 --bots kite,boss-hunter,tank --report-dir /tmp/softcandy_six_map_matrix/jelly-platform
cargo run -p game_harness -- matrix --content-dir content/base_demo --map-id cracked-star-jar --seconds 600 --seed-start 12345 --seeds 3 --bots kite,boss-hunter,tank --report-dir /tmp/softcandy_six_map_matrix/cracked-star-jar
```

## Next Repair Order

1. soda-creek: reduce early Tank deaths without making high-skill bots even safer, likely by moving pressure out of early swarms and into readable Boss mechanics.
2. cracked-star-jar: raise final-map pressure and make phase-storm hazards meaningful.
3. frosting-grassland: add gentle late pressure while preserving beginner readability.
4. cotton-cloud-pasture and jelly-platform: tune BossHunter/Tank pressure after the first three maps are stable.
