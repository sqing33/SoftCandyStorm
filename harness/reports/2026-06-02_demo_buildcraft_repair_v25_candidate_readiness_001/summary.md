# v25 Candidate Readiness

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Decision: `candidate_waiting_for_human_evidence`
- Design review: `design_review_incomplete`
- Manual playtest: `manual_playtest_incomplete`
- Manual reports: `0` / `9`

## Next Actions

- Fill the v25 design review draft for pudding-turret, then run `python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete`.
- Run the next human playtest with `python3 harness/playtest/run_v25_manual_playtest.py new_001`.
- Start v25 playable-content repair triage with `python3 harness/playtest/play_v25_candidate.py default`.
- Refresh the repair triage packet with `python3 harness/playtest/create_v25_content_repair_action_plan.py` after new local reports.

## Next Manual Command

- `python3 harness/playtest/run_v25_manual_playtest.py new_001`
- Runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25001 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_001.json --capture-interval 2`

## Blockers

- `design_review_incomplete`
- `manual_playtest_incomplete`

## Design Review

- Draft has placeholder: `True`
- Placeholder reviews: `pudding-turret`

## Manual Playtest

- Draft has TODO: `True`
- Missing reports: `9`
- `harness/telemetry/local/v25_manual_playtest_new_001.json`
- `harness/telemetry/local/v25_manual_playtest_new_002.json`
- `harness/telemetry/local/v25_manual_playtest_new_003.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_001.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_002.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_003.json`
- `harness/telemetry/local/v25_manual_playtest_build_001.json`
- `harness/telemetry/local/v25_manual_playtest_build_002.json`
- `harness/telemetry/local/v25_manual_playtest_build_003.json`

## Content Repair Plan

- Decision: `v25_content_repair_action_plan_needs_playtest_reports`
- Action items: `26`
- Missing reports: `21`
- Report attention: `0`
- Objective metric risks: `0`
- Content coverage gaps: `5`
- Next commands:
  - `python3 harness/playtest/play_v25_candidate.py default`
  - `python3 harness/playtest/run_v25_manual_playtest.py new_001`
  - `python3 harness/playtest/run_v25_manual_playtest.py new_002`
  - `python3 harness/playtest/run_v25_manual_playtest.py new_003`
  - `python3 harness/playtest/run_v25_manual_playtest.py skilled_001`

## Limitations

- This readiness report only combines local status checks.
- It does not fill human review evidence, play the game, judge fun, or promote content.
- The content repair plan is triage only; it does not add acceptance evidence or promote v25.
- v25 must not be copied into content/base_demo, accepted_content, or Runtime official content before human gates pass.
