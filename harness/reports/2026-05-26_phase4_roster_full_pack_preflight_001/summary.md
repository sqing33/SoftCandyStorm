# Materialized Content Pack Preflight

- Root: `harness/generated_candidates`
- Decision: `materialized_content_packs_valid`
- Candidate count: 1
- Content count: 72

## Candidates

| Candidate | Decision | Content | Errors | Warnings |
|---|---|---:|---:|---:|
| `2026-05-26_phase4_roster_gap_full_pack` | `valid` | 72 | 0 | 0 |

## Errors

- None

## Warnings

- None

## Limitations

- This preflight checks generated candidate structure and references only.
- A passing report does not validate gameplay semantics, budgets, simulations, replay regression, or human review.
- Full promotion still requires game_harness validate-candidates when the Rust binary can launch.
