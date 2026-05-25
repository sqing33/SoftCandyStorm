# Release Evidence Tools

This directory stores release candidate evidence manifests. These manifests do
not run the game or replace Harness results; they prevent a release candidate
from being called ready unless every required gate has explicit evidence.

## Validate Current Evidence

```bash
python3 tools/validate_release_candidate_evidence.py \
  harness/release/current_local_rc_evidence.json \
  --repo-root . \
  --report /tmp/release_candidate_evidence.json \
  --markdown /tmp/release_candidate_evidence.md
```

The current local manifest is expected to report `release_candidate_not_ready`
while the local Mach-O binary launch blocker remains unresolved.

Use `--allow-not-ready` when recording a known not-ready report in
`harness/reports/`; do not use it as a release approval.

## Required Gates

- `content_frozen`
- `compile`
- `unit_tests`
- `headless_simulation`
- `multi_seed_no_deadlock`
- `content_schema`
- `static_budget`
- `bot_matrix`
- `replay_regression`
- `performance`
- `manual_playtest`
- `asset_provenance`
- `failure_case_review`
- `release_package`

Every passing gate must point to real, non-synthetic evidence paths.
