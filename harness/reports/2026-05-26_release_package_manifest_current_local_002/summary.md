# Release Package Manifest Validation

- Source: `harness/release/current_local_package_manifest.json`
- Package: `current-local-package-2026-05-26`
- Candidate: `current-local-2026-05-26`
- Release stage: `prototype-local`
- Package status: `blocked`
- Decision: `release_package_not_ready`

## Package Items

| Item | Kind | SHA-256 | Synthetic |
|---|---|---|---|

## Checks

| Check | Status | Evidence | Synthetic |
|---|---|---:|---|
| `package_created` | `blocked` | 1 | False |
| `final_smoke` | `blocked` | 1 | False |

## Missing Ready Items

- `asset_manifest`
- `checksum_manifest`
- `content_lockfile`
- `release_archive`
- `release_notes`
- `runtime_bundle`

## Missing Ready Checks

- `asset_manifest_verified`
- `checksum_recorded`
- `content_lock_verified`
- `release_notes_reviewed`

## Blockers

- package_status is `blocked`
- package_created: check status is `blocked`
- final_smoke: check status is `blocked`
- package blocker: local_binary_launch_blocked
- package blocker: release_candidate_not_ready

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks release package evidence only; it does not build, sign, launch, or upload packages.
- A ready package still needs the release candidate evidence manifest to pass every release gate.
- Draft or blocked package manifests are allowed as honest not-ready evidence, not as release approval.
