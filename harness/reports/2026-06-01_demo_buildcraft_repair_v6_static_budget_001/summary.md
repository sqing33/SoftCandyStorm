# Static Balance Budget Validation

- Source: `harness/generated_candidates/2026-06-01_demo_buildcraft_repair_v6_full_pack`
- Decision: `static_balance_budget_valid`
- Weapons: 17
- Enemies: 12
- Bosses: 6
- Waves: 6

## Errors

- None

## Warnings

- enemy `sprinkle-spitter` declared threat 2.20 differs from computed threat 1.05

## Limitations

- This validator mirrors first-pass static budget checks only.
- It does not run GameCore, Bot simulations, replay regression, performance tests, or human playtests.
- A valid static budget report is not sufficient to promote content into accepted_content.
