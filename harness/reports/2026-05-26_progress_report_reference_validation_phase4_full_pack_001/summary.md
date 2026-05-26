# Progress Report Reference Validation

- Source: `harness/progress.json`
- Decision: `progress_reports_valid`
- Items: 289
- Report references: 286 / 286
- Items without report: 0

## Sections

| Section | Items |
|---|---:|
| `completed` | 211 |
| `current_findings` | 75 |
| `next_recommended` | 3 |

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks progress ledger structure and local report path existence only.
- It does not prove the referenced report's conclusions are correct or still current.
- Older completed entries without a report are warnings, not errors, until backfilled.
