# Demo Wave Identity Candidates

- Status: generated candidate patch only
- Accepted content: false
- Runtime integrated: false
- Goal: turn the existing Phase 4 enemy/passive roster fill into a more playable Demo Content Pack v0.1 candidate by giving all six maps stronger wave identity.

This patch reuses the four Phase 4 passive candidates and four enemy candidates, then overrides the six standard waves so the new enemies appear gradually after the early teaching window.

Required next gates:

1. Partial candidate validation with `--allow-overrides`.
2. Materialize into a full generated candidate pack with `--allow-overrides`.
3. Materialized pack preflight and static budget review.
4. `game_harness validate-candidates`, Bot simulation, Replay regression.
5. Human design review and manual playtest before acceptance.
