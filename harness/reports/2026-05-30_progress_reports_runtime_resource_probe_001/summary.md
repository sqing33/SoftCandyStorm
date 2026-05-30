# Progress Report Reference Validation

- Source: `harness/progress.json`
- Decision: `progress_reports_valid`
- Items: 579
- Report references: 570 / 570
- Items without report: 0

## Sections

| Section | Items |
|---|---:|
| `completed` | 252 |
| `current_findings` | 318 |
| `next_recommended` | 9 |

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks progress ledger structure and local report path existence only.
- It does not prove the referenced report's conclusions are correct or still current.
- Older completed entries without a report are warnings, not errors, until backfilled.
