# Playtest Review Tools

This directory stores manual playtest templates and validators. These files do
not replace human review; they check that a human-filled review has enough
evidence to support a playtest or content acceptance decision.

## Validate A Review

```bash
python3 harness/playtest/validate_manual_review.py \
  harness/playtest/content_acceptance_review_template.json \
  --strict-acceptance \
  --report /tmp/manual_review_validation.json \
  --markdown /tmp/manual_review_validation.md
```

The bundled templates are intentionally incomplete and should fail validation
until a human fills every required rating, notes, tags, and next action field.

## Run Regression Tests

```bash
python3 harness/playtest/test_validate_manual_review.py
```

The tests use bundled positive and negative fixtures. They verify strict
acceptance validation, CLI exit codes, and JSON/Markdown report output without
requiring Rust, Bevy, GameCore, or local binary launch.

## Gate Rules

- A valid review needs the 9 required run ids: `new_001` to `build_003`.
- Rating fields must be integers from 1 to 5.
- `notes` must contain a concrete human observation.
- `next_actions` must be a non-empty list of actionable strings.
- Run gate decisions may only be `repair`, `playtest_pass`, or `needs_more_runs`.
- `accept_candidate` in strict acceptance mode requires candidate id, content hash,
  reviewer, review date, summary, and all provided runs marked `playtest_pass`.

The validator outputs `manual_review_valid` or `manual_review_invalid`. It only
checks evidence completeness; it cannot judge whether the game is fun.
