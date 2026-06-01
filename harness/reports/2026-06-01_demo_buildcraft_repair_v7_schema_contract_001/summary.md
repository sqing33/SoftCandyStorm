# Content Schema Contract Validation

- Schema manifest: `content/schemas/manifest.json`
- Decision: `content_schema_contract_valid`
- Schemas: 9 / 9
- Content packs: 1
- Semantic checks: 340

## Content Packs

| Content Dir | Decision | Items | Semantic Checks |
|---|---|---:|---:|
| `harness/generated_candidates/2026-06-01_demo_buildcraft_repair_v7_full_pack` | `content_schema_contract_valid` | 87 | 340 |

## Errors

- None

## Warnings

- None

## Limitations

- This validator supports the JSON Schema subset used in content/schemas only.
- It checks structural contract, required fields, enums, id patterns, simple numeric bounds, cross-file references, and basic timing/range semantics.
- It does not run GameCore loading, static budget gates, Bot simulation, Replay regression, or human review.
