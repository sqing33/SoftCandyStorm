# Progress Report Reference Validation

- Source: `harness/progress.json`
- Decision: `progress_reports_valid`
- Items: 448
- Report references: 445 / 445
- Items without report: 0

## Sections

| Section | Items |
|---|---:|
| `completed` | 232 |
| `current_findings` | 213 |
| `next_recommended` | 3 |

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks progress ledger structure and local report path existence only.
- It does not prove the referenced report's conclusions are correct or still current.
- Older completed entries without a report are warnings, not errors, until backfilled.
