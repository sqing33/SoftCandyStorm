# Manual Platform Path Review Validation

- Source: `harness/save_contract/manual_platform_path_review_template.json`
- Decision: `manual_platform_path_review_invalid`
- Gate decision: `needs_more_review`
- Checks reviewed: 7 / 7
- Issue checks: 7
- Global risks: 1

## Errors

- review_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- logical_roots: notes must not contain TODO or placeholder markers
- logical_roots: required_changes must not contain TODO or placeholder markers
- no_host_absolute_paths: notes must not contain TODO or placeholder markers
- no_host_absolute_paths: required_changes must not contain TODO or placeholder markers
- delete_scope: notes must not contain TODO or placeholder markers
- delete_scope: required_changes must not contain TODO or placeholder markers
- export_scope: notes must not contain TODO or placeholder markers
- export_scope: required_changes must not contain TODO or placeholder markers
- migration_original_retention: notes must not contain TODO or placeholder markers
- migration_original_retention: required_changes must not contain TODO or placeholder markers
- cloud_sync_policy: notes must not contain TODO or placeholder markers
- cloud_sync_policy: required_changes must not contain TODO or placeholder markers
- runtime_evidence_limits: notes must not contain TODO or placeholder markers
- runtime_evidence_limits: required_changes must not contain TODO or placeholder markers
- global_risks must not contain TODO or placeholder markers
- next_actions must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks manual platform path review completeness only.
- It does not provide legal advice, platform approval, cloud save approval, or release readiness.
- A pass decision does not prove executable Runtime platform path behavior.
