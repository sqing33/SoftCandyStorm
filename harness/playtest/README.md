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

## Create A Draft

```bash
python3 harness/playtest/create_manual_playtest_review_draft.py \
  --template harness/playtest/runtime_manual_review_template.json \
  --candidate-id current-base-demo-runtime \
  --content-hash TODO:content-hash-after-freeze \
  --out harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json
```

The generated draft covers the 9 required playtest runs and defaults to
`needs_more_runs`. It contains `TODO` ratings by design, so
`validate_manual_review.py --strict-acceptance` rejects it until a human
playtester fills concrete observations.

## Create A Review Packet

```bash
python3 harness/playtest/create_manual_playtest_review_packet.py \
  --template harness/playtest/runtime_manual_review_template.json \
  --draft harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json \
  --repo-root . \
  --out harness/reports/2026-05-26_runtime_manual_playtest_review_packet_001/summary.md
```

The packet gathers the 9-run matrix, required observations, TODO draft status,
rating fields, allowed tags, and gate labels into one Markdown file. It does
not run Runtime, fill ratings, approve a candidate, or replace the strict
acceptance validator.

## Launch The v25 Manual Playtest Candidate

The current Demo buildcraft repair v25 candidate has a dedicated manual
launcher:

```bash
python3 harness/playtest/check_v25_candidate_readiness.py --allow-incomplete
python3 harness/playtest/list_v25_human_evidence_todos.py --allow-todos
python3 harness/playtest/run_v25_manual_playtest.py --list
python3 harness/playtest/run_v25_manual_playtest.py --status
python3 harness/playtest/run_v25_manual_playtest.py --next --dry-run
python3 harness/playtest/run_v25_manual_playtest.py --next
python3 harness/playtest/run_v25_manual_playtest.py new_001 --dry-run
python3 harness/playtest/run_v25_manual_playtest.py new_001
python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete
```

The launcher targets
`harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack`
and writes reports under `harness/telemetry/local/`. It intentionally does not
add `--demo-input`, `--simulation-speed`, or `--auto-exit-after-report`, because
those flags would make the evidence automated rather than human playtest
evidence.

Use `check_v25_candidate_readiness.py` for the combined current-state summary:
design-review TODO status, manual report counts, blockers, and the next manual
playtest command.

Use `list_v25_human_evidence_todos.py` to list every design-review and
manual-playtest TODO field that must be replaced by concrete human evidence.

Use `--status` to see local report progress and `--next` to launch the first
run whose local report is still missing. These shortcuts only inspect local
report files; the stricter status checker still verifies draft TODOs and
candidate metadata.

After running manual sessions and filling the draft, use
`check_v25_manual_playtest_status.py` to confirm that all 9 local reports exist
and the draft no longer contains TODO placeholders before running strict
acceptance validation.

## Create An Acceptance Evidence Packet

```bash
python3 harness/playtest/create_manual_playtest_acceptance_review_packet.py \
  --repo-root . \
  --report harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/manual_playtest_acceptance_review_packet.json \
  --markdown harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/summary.md
```

Before generating that packet for the current local draft, keep the strict
validation report as evidence:

```bash
python3 harness/playtest/validate_manual_review.py \
  harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json \
  --strict-acceptance \
  --report harness/reports/2026-05-26_runtime_manual_playtest_strict_validation_current_local_001/manual_review_validation.json \
  --markdown harness/reports/2026-05-26_runtime_manual_playtest_strict_validation_current_local_001/summary.md
```

The current local acceptance packet is intentionally
`manual_playtest_acceptance_review_packet_needs_evidence`: the draft still has
TODO ratings, strict validation is `manual_review_invalid`, and the release
candidate `manual_playtest` gate remains `waiting`.

## Run Regression Tests

```bash
python3 harness/playtest/test_create_manual_playtest_review_draft.py
python3 harness/playtest/test_create_manual_playtest_review_packet.py
python3 harness/playtest/test_create_manual_playtest_acceptance_review_packet.py
python3 harness/playtest/test_check_v25_candidate_readiness.py
python3 harness/playtest/test_list_v25_human_evidence_todos.py
python3 harness/playtest/test_check_v25_manual_playtest_status.py
python3 harness/playtest/test_run_v25_manual_playtest.py
python3 harness/playtest/test_validate_manual_review.py
```

The tests use bundled positive and negative fixtures. They verify strict
acceptance validation, draft generation, CLI exit codes, and JSON/Markdown
report output without requiring Rust, Bevy, GameCore, or local binary launch.

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
