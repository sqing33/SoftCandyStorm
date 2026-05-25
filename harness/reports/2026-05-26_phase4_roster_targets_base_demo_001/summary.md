# Phase 4 Roster Target Validation

- Content dir: `content/base_demo`
- Decision: `phase4_roster_targets_invalid`

## Counts

| Category | Count | Target |
|---|---:|---:|
| `characters` | 5 | 5 |
| `weapons` | 12 | 12 |
| `passives` | 8 | 12 |
| `evolutions` | 8 | 8 |
| `enemies` | 8 | 12 |
| `bosses` | 6 | 3 |
| `maps` | 6 | 1 |
| `waves` | 6 | 1 |

## Errors

- passives count 8 is below Phase 4 target 12
- enemies count 8 is below Phase 4 target 12

## Warnings

- weapons has 2 extra ids beyond docs/04 named roster

## Limitations

- This validator checks docs/04 roster coverage, docs/12 Phase 4 counts, required fields, and lightweight references only.
- It does not replace GameCore schema validation, static budget gates, Bot simulation, replay regression, or human review.
