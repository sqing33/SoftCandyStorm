# Opening Boundary Escape Reward Profile

- Decision: `profile_ready_for_probe`
- Profile: `opening-boundary-escape`
- Scope: 0-60s opening repair only

## What Changed

`opening-boundary-escape` keeps the existing opening route-recovery profile behavior and adds one extra pressure-gated shaping component:

- active only before `60s`
- active only when boundary edge risk and enemy pressure are both high
- rewards moving back toward the map interior
- penalizes continuing outward into the pressured edge
- contributes through a separate `opening_boundary_escape` reward-breakdown field

This is intended to target seed `63402` style failures where the policy remains locked on an unsafe edge action after enemy pressure rises. It is not a policy gate and does not replace fixed-window validation.

## Verification

- `cargo fmt --check`
- `cargo test -p game_harness`
- `env PYTHONPATH=. python3 python/gym_env/test_soft_candy_env.py`
- `env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache python3 python/train/train_sb3.py --algorithm ppo --dry-run --reward-profile opening-boundary-escape --report harness/reports/2026-05-30_opening_boundary_escape_profile_001/dry_run.json`

## Next Step

Run a conservative 256 timestep stage 01 probe from the parent-preserving opening-route-recovery setting, then require same-seed 60/180/300 second parent no-regression before considering any stage 02 handoff.
