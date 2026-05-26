# Demo Readiness Audit

- Source: `docs/01 first-demo target`
- Decision: `demo_not_ready`
- Gates: 11

## Status Counts

| Status | Count |
|---|---:|
| `blocked` | 2 |
| `pass` | 2 |
| `waiting` | 7 |

## Gates

| Gate | Status | Summary | Evidence |
|---|---|---|---:|
| `formal_content_pack` | `blocked` | content shape is not sufficient for a demo-ready formal content pack | 1 |
| `candidate_content_pack` | `pass` | content counts and build tags satisfy docs/01 demo shape | 1 |
| `candidate_full_pack` | `waiting` | Phase 4 full pack candidate reaches demo roster shape but remains candidate-only | 1 |
| `schema_preflight` | `waiting` | candidate full pack preflight exists; formal Rust/GameCore schema gate remains blocked by local binary launch | 2 |
| `static_budget` | `waiting` | pure Python static budgets exist for base_demo and full pack; game_harness budget-content still needs binary recovery | 2 |
| `historical_bot_matrix` | `waiting` | historical 9-bot 20-seed matrix and replay regression exist, but current binary blocker prevents fresh release evidence | 2 |
| `runtime_capture` | `waiting` | historical Runtime captures prove wiring but not current playable demo readiness | 3 |
| `prototype_assets` | `pass` | programmatic top-down prototype assets cover core demo readability placeholders | 1 |
| `meta_progression` | `waiting` | meta progression smoke and save contracts exist, but complete base UI and fresh runtime validation remain missing | 3 |
| `manual_playtest` | `waiting` | 9-run manual playtest draft, packet, strict validation, and acceptance evidence packet exist, but TODO ratings are not acceptance evidence | 4 |
| `release_state` | `blocked` | release candidate is not ready and accepted content lockfile is empty/blocked | 2 |

## Content Counts

| Category | Formal | Candidate | Target |
|---|---:|---:|---:|
| `characters` | 5 | 5 | 1 |
| `maps` | 6 | 6 | 1 |
| `weapons` | 12 | 12 | 12 |
| `passives` | 8 | 12 | 8 |
| `enemies` | 8 | 12 | 12 |
| `bosses` | 6 | 6 | 3 |

## Build Groups

| Group | Formal Items | Candidate Items |
|---|---|---|
| `projectile` | candy-crystal-lance, frosting-gloves, lollipop-boomerang, rainbow-candy-shot, soda-bubble-pop, star-sugar-ray | candy-crystal-lance, frosting-gloves, jelly-lens-polish, lollipop-boomerang, rainbow-candy-shot, soda-bubble-pop, star-sugar-ray |
| `defense` | big-candy-jar, marshmallow-shield, mint-cyclone, nonstick-apron | big-candy-jar, cocoa-safety-badge, honey-heart, marshmallow-shield, mint-cyclone, nonstick-apron |
| `control` | caramel-sticky-ground, mint-cyclone, sour-plum-spray, sour-tuner | caramel-sticky-ground, mint-cyclone, peppermint-pocket-watch, sour-plum-spray, sour-tuner |
| `burst` | popping-candy-mine, soda-fountain | popping-candy-mine, soda-fountain |
| `summon` | pudding-turret | pudding-turret |
| `boss` | candy-crystal-lance, star-sugar-ray | candy-crystal-lance, star-sugar-ray |
| `economy` | candy-crystal-lens, star-spoon | candy-crystal-lens, star-spoon |

## Blockers

- formal_content_pack: content shape is not sufficient for a demo-ready formal content pack
- candidate_full_pack: Phase 4 full pack candidate reaches demo roster shape but remains candidate-only
- schema_preflight: candidate full pack preflight exists; formal Rust/GameCore schema gate remains blocked by local binary launch
- static_budget: pure Python static budgets exist for base_demo and full pack; game_harness budget-content still needs binary recovery
- historical_bot_matrix: historical 9-bot 20-seed matrix and replay regression exist, but current binary blocker prevents fresh release evidence
- runtime_capture: historical Runtime captures prove wiring but not current playable demo readiness
- meta_progression: meta progression smoke and save contracts exist, but complete base UI and fresh runtime validation remain missing
- manual_playtest: 9-run manual playtest draft, packet, strict validation, and acceptance evidence packet exist, but TODO ratings are not acceptance evidence
- release_state: release candidate is not ready and accepted content lockfile is empty/blocked

## Errors

- None

## Warnings

- None

## Limitations

- This audit checks repository evidence for the docs/01 demo target only.
- It does not execute Rust, Bevy, Harness simulation, Replay, performance tests, or manual playtests.
- Candidate content and historical smoke reports cannot prove a release-ready demo.
- A demo_ready decision requires every gate to pass with current, non-candidate evidence.
