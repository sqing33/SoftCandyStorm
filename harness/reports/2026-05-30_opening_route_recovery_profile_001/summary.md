# Opening Route Recovery Reward Profile

- Decision: `opening_route_recovery_profile_ready_for_probe`
- Scope: Rust `gym-bridge`, Python Gym wrapper, SB3 CLI, docs
- Profile: `opening-route-recovery`

## Purpose

`opening-route-recovery` is a repair-only reward profile for 0-60 second opening failures such as seed `63402`, where the policy becomes pinned to a map boundary and locks into action `5` under rising enemy pressure.

The profile keeps the existing base reward components but, only during the opening window, amplifies route recovery, safety-risk reduction, low-health, boundary, enemy-pressure, and action-repeat signals. It also adds a small opening-window defeat penalty. It does not change any RL acceptance gate.

## Validation

- `cargo fmt --check`
- `cargo test -p game_harness`
- `env PYTHONPATH=. python3 python/gym_env/test_soft_candy_env.py`
- `python3 python/train/train_sb3.py --algorithm ppo --dry-run --reward-profile opening-route-recovery --report harness/reports/2026-05-30_opening_route_recovery_profile_001/dry_run.json`

## Next

Run a small stage 01 probe from the e30 mid-anchor guarded parent using `--reward-profile opening-route-recovery`, train seeds `63400-63402`, and then rerun same-seed 60 / 180 / 300 second parent no-regression before considering any stage 02 work.
