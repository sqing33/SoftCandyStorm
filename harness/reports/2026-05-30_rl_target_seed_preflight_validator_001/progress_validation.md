# Progress Report Reference Validation

- Source: `harness/progress.json`
- Decision: `progress_reports_valid`
- Items: 596
- Report references: 585 / 585
- Items without report: 0

## Sections

| Section | Items |
|---|---:|
| `completed` | 263 |
| `current_findings` | 322 |
| `next_recommended` | 11 |

## Errors

- None

## Warnings

- progress id `rl_stage01_seed63402_guard_anchor_strength_probe` appears in multiple sections: completed[261], current_findings[320]
- progress id `rl_target_seed_preflight_validator` appears in multiple sections: completed[262], current_findings[321]

## Limitations

- This validator checks progress ledger structure and local report path existence only.
- It does not prove the referenced report's conclusions are correct or still current.
- Older completed entries without a report are warnings, not errors, until backfilled.
