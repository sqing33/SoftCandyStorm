# Materialized Content Candidate Pack

- Source patch: `harness/generated_candidate_patches/2026-06-01_demo_wave_identity_candidates`
- Base content: `content/base_demo`
- Output: `harness/generated_candidates/2026-06-01_demo_wave_identity_full_pack`
- Allow overrides: True

## Overlay Counts

- `enemies`: 4
- `passives`: 4
- `waves`: 6 (6 overrides)

## Copied Base Counts

- `bosses`: 6
- `characters`: 5
- `enemies`: 8
- `events`: 5
- `evolutions`: 8
- `maps`: 6
- `passives`: 8
- `waves`: 6
- `weapons`: 12

## Limitations

- This command only materializes a generated candidate pack; it does not validate, simulate, accept, or runtime-integrate the content.
- Full validation still requires `game_harness validate-candidates`.
