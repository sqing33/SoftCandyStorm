# Accepted Content Lock Summary

- Status: `locked`
- Accepted dir: `/tmp/soft-candy-lock-accepted.wFhN5X/accepted`
- Lock file: `/tmp/soft-candy-lock-accepted.wFhN5X/accepted/accepted_content.lock.json`
- Runtime content root: `/tmp/soft-candy-lock-accepted.wFhN5X/accepted`
- Result: `1` locked, `0` blocked, `1` total

| Candidate | Status | Objects | Content Hash | Review Runs | Average Rating | Runtime Path | Errors |
|---|---|---:|---|---:|---:|---|---:|
| base-demo-smoke | locked | 14 | fnv1a64:3dcabd9e6da409df | 9 | 4.00 | /tmp/soft-candy-lock-accepted.wFhN5X/accepted/base-demo-smoke | 0 |

## Gate Notes

- The lockfile is written only when every accepted candidate remains valid.
- Each locked entry preserves content hash, acceptance gate, manual review reference, object count, and Runtime content path.
- This command does not invent human review evidence and does not promote playtest candidates.
