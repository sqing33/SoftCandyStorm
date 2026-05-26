# Generated Asset Candidates

This directory is the only allowed landing zone for AI-generated or
post-processed asset candidates before human review. Files here are not accepted
content and must not be wired into Runtime as final art or audio without a later
promotion step.

## Metadata Validation

```bash
python3 tools/validate_asset_candidates.py asset/generated_candidates \
  --report /tmp/asset_candidate_validation.json \
  --markdown /tmp/asset_candidate_validation.md
```

For new `mmx` batches, prefer the stricter command provenance mode:

```bash
python3 tools/validate_asset_candidates.py asset/generated_candidates/<batch> \
  --require-commands
```

The validator checks candidate-only flags, referenced files, prompts or source
provenance, QA notes, batch README files, and review notes. It does not judge
whether the image, voice, or music is good enough.

## Required Batch Shape

Each batch should include:

- `README.md`
- `metadata/manifest.json`
- `metadata/review_<date>.md`
- Original generated files under `images/`, `audio/`, or `music/`
- Processed files only under the same candidate batch when post-processing is
  needed

Every `mmx` manifest should record the prompt, negative prompt when relevant,
the command used, tool/source metadata, QA status, and required next steps.

## Current mmx Batches

- `2026-05-26_mmx_runtime_topdown_audio_plan`: Runtime 俯视角玩家与 Boss 出场音频候选，含小尺寸预览、8 秒 sting 和语音 / sting 叠放预览。
- `2026-05-26_mmx_level_up_feedback_pack`: 升级反馈图标、中文 TTS 和 3.2 秒 jingle 候选，仍需人工美术 / 听感审查。
