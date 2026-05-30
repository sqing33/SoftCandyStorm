# Progress Report Reference Validation

- Source: `harness/progress.json`
- Decision: `progress_reports_valid`
- Items: 602
- Report references: 589 / 589
- Items without report: 0

## Sections

| Section | Items |
|---|---:|
| `completed` | 265 |
| `current_findings` | 324 |
| `next_recommended` | 13 |

## Errors

- None

## Warnings

- progress id `rl_stage01_seed63402_guard_anchor_strength_probe` appears in multiple sections: completed[261], current_findings[320]
- progress id `rl_target_seed_preflight_validator` appears in multiple sections: completed[262], current_findings[321]
- progress id `rl_stage01_seed63402_success_retention_samples` appears in multiple sections: completed[263], current_findings[322]
- progress id `rl_stage01_seed63402_guard_retention_anchor` appears in multiple sections: completed[264], current_findings[323]

## Limitations

- This validator checks progress ledger structure and local report path existence only.
- It does not prove the referenced report's conclusions are correct or still current.
- Older completed entries without a report are warnings, not errors, until backfilled.
