# Accepted Content Lockfile Validation

- Source: `harness/accepted_content/accepted_content.lock.json`
- Decision: `accepted_content_lockfile_blocked`
- Lock status: `blocked`
- Accepted dir: `harness/accepted_content`
- Runtime content root: `harness/accepted_content`
- Result: 0 locked, 0 blocked, 0 total

## Entries

| Candidate | Status | Objects | Runs | Average Rating | Entry Errors |
|---|---|---:|---:|---:|---:|

## Errors

- None

## Lockfile Notes

- no accepted content has passed human review yet

## Warnings

- None

## Limitations

- This validator checks accepted content lockfile evidence shape and local paths only.
- It does not run Rust GameCore, recompute content hashes, promote candidates, or copy Runtime content.
- A valid lockfile is not release approval; release candidate and package gates still apply.
