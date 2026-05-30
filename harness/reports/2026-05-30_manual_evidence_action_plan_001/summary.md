# Manual Evidence Action Plan

- Source audit: `harness/reports/2026-05-26_manual_evidence_gap_audit_001/manual_evidence_gap_audit.json`
- Source decision: `manual_evidence_gaps_present`
- Decision: `manual_evidence_action_plan_ready`
- Items: 20
- Gaps: 20
- Satisfied: 0

## Domains

| Domain | Gaps | Satisfied | Total |
|---|---:|---:|---:|
| `playtest` | 1 | 0 | 1 |
| `content` | 3 | 0 | 3 |
| `asset` | 6 | 0 | 6 |
| `story` | 4 | 0 | 4 |
| `privacy` | 3 | 0 | 3 |
| `platform` | 1 | 0 | 1 |
| `base_ui` | 1 | 0 | 1 |
| `release` | 1 | 0 | 1 |

## Gap Checklist

### playtest

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `manual_playtest_acceptance` | `gap` | `manual_playtest_acceptance_review_packet_needs_evidence` | Replace TODO playtest draft values with real human ratings, notes, tags, and acceptance evidence. | `harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/manual_playtest_acceptance_review_packet.json` |

Next steps:
- Run the 9 human playtest sessions and replace every TODO rating, note, tag, and next action.
- Run validate_manual_review.py --strict-acceptance and keep a manual_review_valid JSON/Markdown report.
- Update the release candidate manual_playtest gate only after real human evidence exists.
- Use the validated manual review as evidence for content acceptance and accepted content lockfile generation.

### content

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `content_acceptance_manifest` | `gap` | `content_acceptance_manifest_invalid` | Create a manifest backed by valid simulation-candidate, final human acceptance, and accepted-content lockfile reports. | `harness/reports/2026-05-26_content_acceptance_manifest_template_001/content_acceptance_manifest.json` |
| `content_acceptance_packet` | `gap` | `content_acceptance_review_packet_needs_evidence` | Finish human design review, manual playtest acceptance, demo readiness, and accepted-content lock evidence before validation. | `harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/content_acceptance_review_packet.json` |
| `content_final_acceptance` | `gap` | `content_final_acceptance_invalid` | Bind a valid simulation candidate manifest and accepted-content lockfile, then record real final acceptance observations. | `harness/reports/2026-05-26_content_final_acceptance_template_001/content_final_acceptance.json` |

Next steps:
- Create a manifest backed by valid simulation-candidate, final human acceptance, and accepted-content lockfile reports.
- Replace design review TODO values with a real human design review and validate it.
- After binary recovery, run formal Harness validate-candidates, budget-content, Bot simulation, and replay regression.
- Run and fill the 9-run manual playtest review with human ratings and notes.
- Only after strict human acceptance, generate a non-empty accepted content lockfile.
- Bind a valid simulation candidate manifest and accepted-content lockfile, then record real final acceptance observations.

### asset

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `asset_acceptance_manifest` | `gap` | `asset_acceptance_manifest_invalid` | Create a manifest backed by valid runtime-candidate, runtime preview, loudness, and final acceptance evidence. | `harness/reports/2026-05-26_asset_acceptance_manifest_template_001/asset_acceptance_manifest.json` |
| `asset_audio_loudness_review` | `gap` | `asset_audio_loudness_review_invalid` | Record real listening, clipping, loudness, dialogue clarity, and loop/duration-fit observations. | `harness/reports/2026-05-26_asset_audio_loudness_review_template_001/asset_audio_loudness_review.json` |
| `asset_candidate_review_level_up_feedback` | `gap` | `asset_candidate_manual_review_invalid` | Fill the level-up feedback review draft with human visual, listening, provenance, and technical-readiness observations. | `harness/reports/2026-05-26_mmx_level_up_feedback_manual_review_draft_001/asset_manual_review.json` |
| `asset_candidate_review_runtime_topdown_audio` | `gap` | `asset_candidate_manual_review_invalid` | Replace generated review draft ratings and TODO notes with real art/audio review observations. | `harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_manual_review_draft_001/asset_candidate_manual_review.json` |
| `asset_final_acceptance` | `gap` | `asset_final_acceptance_invalid` | Bind passing Runtime preview and audio loudness reviews before recording final asset acceptance. | `harness/reports/2026-05-26_asset_final_acceptance_template_001/asset_final_acceptance.json` |
| `asset_runtime_preview_review` | `gap` | `asset_runtime_preview_review_invalid` | Preview staged runtime candidates in context and record concrete small-size/readability observations. | `harness/reports/2026-05-26_asset_runtime_preview_review_template_001/asset_runtime_preview_review.json` |

Next steps:
- Create a manifest backed by valid runtime-candidate, runtime preview, loudness, and final acceptance evidence.
- Record real listening, clipping, loudness, dialogue clarity, and loop/duration-fit observations.
- Fill the level-up feedback review draft with human visual, listening, provenance, and technical-readiness observations.
- Replace generated review draft ratings and TODO notes with real art/audio review observations.
- Bind passing Runtime preview and audio loudness reviews before recording final asset acceptance.
- Preview staged runtime candidates in context and record concrete small-size/readability observations.

### story

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `story_codex_acceptance_manifest` | `gap` | `story_codex_acceptance_manifest_invalid` | Create a manifest backed by valid UI-candidate, Runtime UI review, and final human acceptance evidence. | `harness/reports/2026-05-26_story_codex_acceptance_manifest_template_001/story_codex_acceptance_manifest.json` |
| `story_codex_final_acceptance` | `gap` | `story_codex_final_acceptance_invalid` | Bind a passing Runtime UI review and record final human acceptance for story/codex text. | `harness/reports/2026-05-26_story_codex_final_acceptance_template_001/story_codex_final_acceptance.json` |
| `story_codex_runtime_ui_review` | `gap` | `story_codex_runtime_ui_review_invalid` | Review the F3 candidate metadata UI in Runtime and record concrete observations without loading generated body text. | `harness/reports/2026-05-26_story_codex_runtime_ui_review_template_001/story_codex_runtime_ui_review.json` |
| `story_codex_ui_candidate_manifest` | `gap` | `story_codex_ui_candidate_manifest_invalid` | Complete real story/codex manual review before promoting the text pack to UI-candidate staging. | `harness/reports/2026-05-26_story_codex_ui_candidate_manifest_template_001/story_codex_ui_candidate_manifest.json` |

Next steps:
- Create a manifest backed by valid UI-candidate, Runtime UI review, and final human acceptance evidence.
- Bind a passing Runtime UI review and record final human acceptance for story/codex text.
- Review the F3 candidate metadata UI in Runtime and record concrete observations without loading generated body text.
- Complete real story/codex manual review before promoting the text pack to UI-candidate staging.

### privacy

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `manual_legal_review` | `gap` | `manual_legal_review_invalid` | Complete real legal/compliance review after privacy and platform-path reviews are passing. | `harness/reports/2026-05-26_manual_legal_review_template_001/manual_legal_review.json` |
| `manual_privacy_review` | `gap` | `manual_privacy_review_invalid` | Fill the privacy review with real checks for consent, prohibited fields, notices, retention, and local data controls. | `harness/reports/2026-05-26_manual_privacy_review_template_001/manual_privacy_review.json` |
| `telemetry_privacy_acceptance_packet` | `gap` | `telemetry_privacy_acceptance_review_packet_needs_evidence` | Bring policy, runtime contract, upload transport, platform path, privacy, legal, and RC telemetry gate evidence to passing state. | `harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/telemetry_privacy_acceptance_review_packet.json` |

Next steps:
- Complete real legal/compliance review after privacy and platform-path reviews are passing.
- Fill the privacy review with real checks for consent, prohibited fields, notices, retention, and local data controls.
- Replace TODO placeholders in manual privacy, platform path, and legal/compliance review records.
- Run each manual review validator and keep valid JSON/Markdown reports.
- Implement or explicitly remove upload transport from the release scope, then attach Runtime evidence for the chosen path.
- Update the Release Candidate telemetry_privacy gate only after real human review and Runtime evidence exist.

### platform

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `manual_platform_path_review` | `gap` | `manual_platform_path_review_invalid` | Review logical roots, delete/export scope, migration retention, cloud sync limits, and Runtime evidence limits on the target platform. | `harness/reports/2026-05-26_manual_platform_path_review_template_001/manual_platform_path_review.json` |

Next steps:
- Review logical roots, delete/export scope, migration retention, cloud sync limits, and Runtime evidence limits on the target platform.

### base_ui

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `base_ui_manual_review` | `gap` | `base_ui_manual_review_invalid` | Review F1-F4 base UI flows, local data controls, candidate boundaries, and evidence limits with concrete human observations. | `harness/reports/2026-05-26_base_ui_manual_review_template_001/base_ui_manual_review.json` |

Next steps:
- Review F1-F4 base UI flows, local data controls, candidate boundaries, and evidence limits with concrete human observations.

### release

| Requirement | Status | Decision | Required action | Source |
|---|---|---|---|---|
| `release_candidate_evidence` | `gap` | `release_candidate_not_ready` | Clear every release gate, including compile, tests, Harness, Replay, performance, manual reviews, content, asset, privacy, and package gates. | `harness/reports/2026-05-26_release_candidate_evidence_current_local_004/release_candidate_evidence.json` |

Next steps:
- Clear every release gate, including compile, tests, Harness, Replay, performance, manual reviews, content, asset, privacy, and package gates.

## Evidence Sources

### playtest

- `manual_playtest_acceptance`
  - `harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/manual_playtest_acceptance_review_packet.json`
  - `harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/summary.md`

### content

- `content_acceptance_manifest`
  - `harness/reports/2026-05-26_content_acceptance_manifest_template_001/content_acceptance_manifest.json`
  - `harness/reports/2026-05-26_content_acceptance_manifest_template_001/summary.md`
- `content_acceptance_packet`
  - `harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/content_acceptance_review_packet.json`
  - `harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/summary.md`
- `content_final_acceptance`
  - `harness/reports/2026-05-26_content_final_acceptance_template_001/content_final_acceptance.json`
  - `harness/reports/2026-05-26_content_final_acceptance_template_001/summary.md`

### asset

- `asset_acceptance_manifest`
  - `harness/reports/2026-05-26_asset_acceptance_manifest_template_001/asset_acceptance_manifest.json`
  - `harness/reports/2026-05-26_asset_acceptance_manifest_template_001/summary.md`
- `asset_audio_loudness_review`
  - `harness/reports/2026-05-26_asset_audio_loudness_review_template_001/asset_audio_loudness_review.json`
  - `harness/reports/2026-05-26_asset_audio_loudness_review_template_001/summary.md`
- `asset_candidate_review_level_up_feedback`
  - `harness/reports/2026-05-26_mmx_level_up_feedback_manual_review_draft_001/asset_manual_review.json`
  - `harness/reports/2026-05-26_mmx_level_up_feedback_manual_review_draft_001/summary.md`
- `asset_candidate_review_runtime_topdown_audio`
  - `harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_manual_review_draft_001/asset_candidate_manual_review.json`
  - `harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_manual_review_draft_001/summary.md`
- `asset_final_acceptance`
  - `harness/reports/2026-05-26_asset_final_acceptance_template_001/asset_final_acceptance.json`
  - `harness/reports/2026-05-26_asset_final_acceptance_template_001/summary.md`
- `asset_runtime_preview_review`
  - `harness/reports/2026-05-26_asset_runtime_preview_review_template_001/asset_runtime_preview_review.json`
  - `harness/reports/2026-05-26_asset_runtime_preview_review_template_001/summary.md`

### story

- `story_codex_acceptance_manifest`
  - `harness/reports/2026-05-26_story_codex_acceptance_manifest_template_001/story_codex_acceptance_manifest.json`
  - `harness/reports/2026-05-26_story_codex_acceptance_manifest_template_001/summary.md`
- `story_codex_final_acceptance`
  - `harness/reports/2026-05-26_story_codex_final_acceptance_template_001/story_codex_final_acceptance.json`
  - `harness/reports/2026-05-26_story_codex_final_acceptance_template_001/summary.md`
- `story_codex_runtime_ui_review`
  - `harness/reports/2026-05-26_story_codex_runtime_ui_review_template_001/story_codex_runtime_ui_review.json`
  - `harness/reports/2026-05-26_story_codex_runtime_ui_review_template_001/summary.md`
- `story_codex_ui_candidate_manifest`
  - `harness/reports/2026-05-26_story_codex_ui_candidate_manifest_template_001/story_codex_ui_candidate_manifest.json`
  - `harness/reports/2026-05-26_story_codex_ui_candidate_manifest_template_001/summary.md`

### privacy

- `manual_legal_review`
  - `harness/reports/2026-05-26_manual_legal_review_template_001/manual_legal_review.json`
  - `harness/reports/2026-05-26_manual_legal_review_template_001/summary.md`
- `manual_privacy_review`
  - `harness/reports/2026-05-26_manual_privacy_review_template_001/manual_privacy_review.json`
  - `harness/reports/2026-05-26_manual_privacy_review_template_001/summary.md`
- `telemetry_privacy_acceptance_packet`
  - `harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/telemetry_privacy_acceptance_review_packet.json`
  - `harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/summary.md`

### platform

- `manual_platform_path_review`
  - `harness/reports/2026-05-26_manual_platform_path_review_template_001/manual_platform_path_review.json`
  - `harness/reports/2026-05-26_manual_platform_path_review_template_001/summary.md`

### base_ui

- `base_ui_manual_review`
  - `harness/reports/2026-05-26_base_ui_manual_review_template_001/base_ui_manual_review.json`
  - `harness/reports/2026-05-26_base_ui_manual_review_template_001/summary.md`

### release

- `release_candidate_evidence`
  - `harness/reports/2026-05-26_release_candidate_evidence_current_local_004/release_candidate_evidence.json`
  - `harness/reports/2026-05-26_release_candidate_evidence_current_local_004/summary.md`

## Limitations

- This action plan organizes human-required evidence gaps only.
- It does not run Runtime, inspect gameplay, fill review fields, approve content, or change release gates.
- Every gap remains blocked until a real human review source passes its validator.
