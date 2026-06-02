# v25 Manual Playtest Status

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Draft: `harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`
- Decision: `manual_playtest_incomplete`
- Reports: `0` / `9`
- Draft has TODO: `True`
- Acceptance decision: `needs_more_runs`

## Runs

| Run | Skill | Seed | Report Exists | Draft TODO |
|---|---|---:|---|---|
| `new_001` | `new` | 25001 | `False` | `True` |
| `new_002` | `new` | 25002 | `False` | `True` |
| `new_003` | `new` | 25003 | `False` | `True` |
| `skilled_001` | `skilled` | 25011 | `False` | `True` |
| `skilled_002` | `skilled` | 25012 | `False` | `True` |
| `skilled_003` | `skilled` | 25013 | `False` | `True` |
| `build_001` | `build` | 25021 | `False` | `True` |
| `build_002` | `build` | 25022 | `False` | `True` |
| `build_003` | `build` | 25023 | `False` | `True` |

## Missing Reports

- `harness/telemetry/local/v25_manual_playtest_new_001.json`
- `harness/telemetry/local/v25_manual_playtest_new_002.json`
- `harness/telemetry/local/v25_manual_playtest_new_003.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_001.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_002.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_003.json`
- `harness/telemetry/local/v25_manual_playtest_build_001.json`
- `harness/telemetry/local/v25_manual_playtest_build_002.json`
- `harness/telemetry/local/v25_manual_playtest_build_003.json`

## Errors

- 9 playtest reports are missing
- review draft still contains TODO placeholders

## Limitations

- This checker only inspects local report file presence and draft TODO status.
- It does not play the game, judge fun, validate ratings, or approve content.
- Strict acceptance still requires validate_manual_review.py --strict-acceptance.
