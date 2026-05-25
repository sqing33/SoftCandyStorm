# Candidate Acceptance Summary

- Source: `/tmp/soft-candy-accepted-gate.Udf24M/playtest`
- Accepted: `/tmp/soft-candy-accepted-gate.Udf24M/accepted`
- Repair: `/tmp/soft-candy-accepted-gate.Udf24M/repair`
- Reviews: `/tmp/soft-candy-accepted-gate.Udf24M/reviews`
- Result: `0` accepted, `0` repair, `1` waiting, `1` total

| Candidate | Decision | Runs | Average Rating | Errors | Destination | Next Step |
|---|---|---:|---:|---:|---|---|
| base-demo-smoke | waiting | 0 | - | 1 | - | complete human playtest review before accepted_content promotion |

## Gate Notes

- `accepted` means the candidate has complete human review evidence and is copied to `accepted_content`.
- `waiting` means the candidate remains in `playtest_candidates` until human review evidence is complete.
- This command still does not turn a candidate into a release candidate; version locking and release gates remain separate.
