# v51 Manual Playtest Status

- Candidate id: `2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Content hash: `fnv1a64:50bd536bd0669e2b`
- Draft: `harness/playtest/drafts/2026-06-04_demo_buildcraft_repair_v51_manual_playtest_review_draft.json`
- Decision: `manual_playtest_incomplete`
- Reports: `0` / `6`
- Draft has TODO: `True`
- Acceptance decision: `needs_more_runs`

## Runs

| Run | Skill | Character | Map | Seed | Report Exists | Draft TODO |
|---|---|---|---|---:|---|---|
| `new_frosting_jar_keeper` | `new` | `jar-keeper` | `frosting-grassland` | 55301 | `False` | `True` |
| `speed_soda_bubble_courier` | `skilled` | `bubble-courier` | `soda-creek` | 55302 | `False` | `True` |
| `summon_cotton_pudding_crafter` | `build` | `pudding-crafter` | `cotton-cloud-pasture` | 55303 | `False` | `True` |
| `control_caramel_sour_plum_doctor` | `skilled` | `sour-plum-doctor` | `caramel-workshop` | 55304 | `False` | `True` |
| `defense_jelly_cream_knight` | `build` | `cream-knight` | `jelly-platform` | 55305 | `False` | `True` |
| `final_cracked_jar_keeper` | `skilled` | `jar-keeper` | `cracked-star-jar` | 55306 | `False` | `True` |

## Missing Reports

- `harness/telemetry/local/v51_manual_playtest_new_frosting_jar_keeper.json`
- `harness/telemetry/local/v51_manual_playtest_speed_soda_bubble_courier.json`
- `harness/telemetry/local/v51_manual_playtest_summon_cotton_pudding_crafter.json`
- `harness/telemetry/local/v51_manual_playtest_control_caramel_sour_plum_doctor.json`
- `harness/telemetry/local/v51_manual_playtest_defense_jelly_cream_knight.json`
- `harness/telemetry/local/v51_manual_playtest_final_cracked_jar_keeper.json`

## Errors

- 6 playtest reports are missing
- review draft still contains TODO placeholders

## Limitations

- This checker only inspects local report file presence and draft TODO status.
- It does not play the game, judge fun, validate ratings, or approve content.
- Strict acceptance still requires human-filled review evidence and validate_manual_review.py --strict-acceptance.
- The current candidate must not be copied into accepted_content or Runtime official content before human gates pass.
