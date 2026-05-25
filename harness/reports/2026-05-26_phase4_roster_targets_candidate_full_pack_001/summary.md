# Phase 4 Roster Target Validation

- Content dir: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack`
- Decision: `phase4_roster_targets_valid`

## Counts

| Category | Count | Target |
|---|---:|---:|
| `characters` | 5 | 5 |
| `weapons` | 12 | 12 |
| `passives` | 12 | 12 |
| `evolutions` | 8 | 8 |
| `enemies` | 12 | 12 |
| `bosses` | 6 | 3 |
| `maps` | 6 | 1 |
| `waves` | 6 | 1 |

## Errors

- None

## Warnings

- weapons has 2 extra ids beyond docs/04 named roster
- passives has 4 extra ids beyond docs/04 named roster
- enemies has 4 extra ids beyond docs/04 named roster

## Limitations

- This validator checks docs/04 roster coverage, docs/12 Phase 4 counts, required fields, and lightweight references only.
- It does not replace GameCore schema validation, static budget gates, Bot simulation, replay regression, or human review.
