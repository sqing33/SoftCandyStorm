# Manual Evidence Gap Audit

- Decision: `manual_evidence_gaps_present`
- Requirements: 20
- Satisfied: 0
- Gaps: 20
- Missing reports: 0

## Domains

| Domain | Satisfied | Gaps | Total |
|---|---:|---:|---:|
| `asset` | 0 | 6 | 6 |
| `base_ui` | 0 | 1 | 1 |
| `content` | 0 | 3 | 3 |
| `platform` | 0 | 1 | 1 |
| `playtest` | 0 | 1 | 1 |
| `privacy` | 0 | 3 | 3 |
| `release` | 0 | 1 | 1 |
| `story` | 0 | 4 | 4 |

## Requirements

| Domain | Requirement | Status | Decision | Gate |
|---|---|---|---|---|
| `playtest` | `manual_playtest_acceptance` | `gap` | `manual_playtest_acceptance_review_packet_needs_evidence` | `-` |
| `content` | `content_acceptance_packet` | `gap` | `content_acceptance_review_packet_needs_evidence` | `-` |
| `content` | `content_final_acceptance` | `gap` | `content_final_acceptance_invalid` | `needs_more_review` |
| `content` | `content_acceptance_manifest` | `gap` | `content_acceptance_manifest_invalid` | `-` |
| `asset` | `asset_candidate_review_runtime_topdown_audio` | `gap` | `asset_candidate_manual_review_invalid` | `needs_more_review` |
| `asset` | `asset_candidate_review_level_up_feedback` | `gap` | `asset_candidate_manual_review_invalid` | `needs_more_review` |
| `asset` | `asset_runtime_preview_review` | `gap` | `asset_runtime_preview_review_invalid` | `needs_more_review` |
| `asset` | `asset_audio_loudness_review` | `gap` | `asset_audio_loudness_review_invalid` | `needs_more_review` |
| `asset` | `asset_final_acceptance` | `gap` | `asset_final_acceptance_invalid` | `needs_more_review` |
| `asset` | `asset_acceptance_manifest` | `gap` | `asset_acceptance_manifest_invalid` | `-` |
| `story` | `story_codex_ui_candidate_manifest` | `gap` | `story_codex_ui_candidate_manifest_invalid` | `-` |
| `story` | `story_codex_runtime_ui_review` | `gap` | `story_codex_runtime_ui_review_invalid` | `needs_more_review` |
| `story` | `story_codex_final_acceptance` | `gap` | `story_codex_final_acceptance_invalid` | `needs_more_review` |
| `story` | `story_codex_acceptance_manifest` | `gap` | `story_codex_acceptance_manifest_invalid` | `-` |
| `privacy` | `manual_privacy_review` | `gap` | `manual_privacy_review_invalid` | `needs_more_review` |
| `platform` | `manual_platform_path_review` | `gap` | `manual_platform_path_review_invalid` | `needs_more_review` |
| `privacy` | `manual_legal_review` | `gap` | `manual_legal_review_invalid` | `needs_more_review` |
| `privacy` | `telemetry_privacy_acceptance_packet` | `gap` | `telemetry_privacy_acceptance_review_packet_needs_evidence` | `-` |
| `base_ui` | `base_ui_manual_review` | `gap` | `base_ui_manual_review_invalid` | `needs_more_review` |
| `release` | `release_candidate_evidence` | `gap` | `release_candidate_not_ready` | `-` |

## Gaps

- `manual_playtest_acceptance` (`playtest`): Replace TODO playtest draft values with real human ratings, notes, tags, and acceptance evidence.
- `content_acceptance_packet` (`content`): Finish human design review, manual playtest acceptance, demo readiness, and accepted-content lock evidence before validation.
- `content_final_acceptance` (`content`): Bind a valid simulation candidate manifest and accepted-content lockfile, then record real final acceptance observations.
- `content_acceptance_manifest` (`content`): Create a manifest backed by valid simulation-candidate, final human acceptance, and accepted-content lockfile reports.
- `asset_candidate_review_runtime_topdown_audio` (`asset`): Replace generated review draft ratings and TODO notes with real art/audio review observations.
- `asset_candidate_review_level_up_feedback` (`asset`): Fill the level-up feedback review draft with human visual, listening, provenance, and technical-readiness observations.
- `asset_runtime_preview_review` (`asset`): Preview staged runtime candidates in context and record concrete small-size/readability observations.
- `asset_audio_loudness_review` (`asset`): Record real listening, clipping, loudness, dialogue clarity, and loop/duration-fit observations.
- `asset_final_acceptance` (`asset`): Bind passing Runtime preview and audio loudness reviews before recording final asset acceptance.
- `asset_acceptance_manifest` (`asset`): Create a manifest backed by valid runtime-candidate, runtime preview, loudness, and final acceptance evidence.
- `story_codex_ui_candidate_manifest` (`story`): Complete real story/codex manual review before promoting the text pack to UI-candidate staging.
- `story_codex_runtime_ui_review` (`story`): Review the F3 candidate metadata UI in Runtime and record concrete observations without loading generated body text.
- `story_codex_final_acceptance` (`story`): Bind a passing Runtime UI review and record final human acceptance for story/codex text.
- `story_codex_acceptance_manifest` (`story`): Create a manifest backed by valid UI-candidate, Runtime UI review, and final human acceptance evidence.
- `manual_privacy_review` (`privacy`): Fill the privacy review with real checks for consent, prohibited fields, notices, retention, and local data controls.
- `manual_platform_path_review` (`platform`): Review logical roots, delete/export scope, migration retention, cloud sync limits, and Runtime evidence limits on the target platform.
- `manual_legal_review` (`privacy`): Complete real legal/compliance review after privacy and platform-path reviews are passing.
- `telemetry_privacy_acceptance_packet` (`privacy`): Bring policy, runtime contract, upload transport, platform path, privacy, legal, and RC telemetry gate evidence to passing state.
- `base_ui_manual_review` (`base_ui`): Review F1-F4 base UI flows, local data controls, candidate boundaries, and evidence limits with concrete human observations.
- `release_candidate_evidence` (`release`): Clear every release gate, including compile, tests, Harness, Replay, performance, manual reviews, content, asset, privacy, and package gates.

## Errors

- None

## Limitations

- This audit reads existing evidence reports only; it does not run Rust, Bevy, Harness simulations, Replay, performance tests, or manual reviews.
- A satisfied row means the referenced machine report has the expected passing decision; it still does not replace release candidate aggregation.
- Template reports and generated drafts with TODO placeholders must remain gaps until a real human fills and validates them.
