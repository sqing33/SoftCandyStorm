# Content Schema Contract Validation

- Schema manifest: `content/schemas/manifest.json`
- Decision: `content_schema_contract_valid`
- Schemas: 9 / 9
- Content packs: 2

## Content Packs

| Content Dir | Decision | Items |
|---|---|---:|
| `content/base_demo` | `content_schema_contract_valid` | 64 |
| `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack` | `content_schema_contract_valid` | 72 |

## Errors

- None

## Warnings

- None

## Limitations

- This validator supports the JSON Schema subset used in content/schemas only.
- It checks structural contract, required fields, enums, id patterns, and simple numeric bounds.
- It does not run GameCore loading, static budget gates, Bot simulation, Replay regression, or human review.
