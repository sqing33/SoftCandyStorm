# v61 Candidate Readiness

- Candidate id: `2026-06-05_demo_buildcraft_repair_v61_full_pack`
- Content hash: `fnv1a64:66fa99c902f3af87`
- Decision: `candidate_waiting_for_human_evidence`
- Design review: `design_review_incomplete`
- Manual playtest: `manual_playtest_incomplete`
- Manual reports: `0` / `6`

## Next Actions

- Fill the current candidate design review draft, then run `python3 harness/content_review/check_current_design_review_status.py --allow-incomplete`.
- Run the next human playtest with `python3 harness/playtest/run_current_manual_playtest.py new_frosting_jar_keeper`.

## Next Manual Command

- `python3 harness/playtest/run_current_manual_playtest.py new_frosting_jar_keeper`
- Runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id jar-keeper --map-id frosting-grassland --seed 55301 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v61_manual_playtest_new_frosting_jar_keeper.json --capture-interval 2`

## Blockers

- `design_review_incomplete`
- `manual_playtest_incomplete`

## Design Review

- Draft has placeholder: `True`
- Placeholder reviews: `route-memory-caramel-ring`

## Manual Playtest

- Draft has TODO: `True`
- Missing reports: `6`
- `harness/telemetry/local/v61_manual_playtest_new_frosting_jar_keeper.json`
- `harness/telemetry/local/v61_manual_playtest_speed_soda_bubble_courier.json`
- `harness/telemetry/local/v61_manual_playtest_summon_cotton_pudding_crafter.json`
- `harness/telemetry/local/v61_manual_playtest_control_caramel_sour_plum_doctor.json`
- `harness/telemetry/local/v61_manual_playtest_defense_jelly_cream_knight.json`
- `harness/telemetry/local/v61_manual_playtest_final_cracked_jar_keeper.json`

## Limitations

- This readiness report only combines local human-evidence status checks.
- It does not fill human review evidence, play the game, judge fun, or promote content.
- Current candidate content must stay out of content/base_demo, accepted_content, and Runtime official content until human gates pass.
