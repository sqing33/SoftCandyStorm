# Terminal Sequence Recovery Reward Profile

- Decision: `terminal_sequence_reward_profile_ready_for_probe`
- Scope: Rust `gym-bridge` reward shaping, Python Gym wrapper, `train_sb3.py`, RL plan helper allow-lists, and RL training docs
- Profile: `terminal-sequence-recovery`

## Result

`terminal-sequence-recovery` is now available as a training reward profile for the caramel terminal-conversion line. It ramps from `180s` to `210s`, then keeps the stronger sequence objective active through the whole `210-300s` terminal window. The profile reuses the late route-recovery safety channels with a stronger component scale, amplifies action-repeat penalties, and adds a larger terminal victory / defeat adjustment.

This profile is meant for the failure shape recorded in `harness/reports/2026-05-31_rl_caramel_selective_ranked_victory_terminal_sequence_diagnostic_001/summary.md`: branch usage and nearest-action agreement are already high, but the online rollout still dies from low-health / hazard pressure. The next probe can now change the online objective instead of continuing simple supervised terminal-path imitation.

## Validation

- `cargo test -p game_harness gym_reward_profile`
- `cargo test -p game_harness gym_terminal_sequence_recovery_profile_focuses_whole_terminal_sequence`
- `env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run --with pytest python -m pytest python/gym_env/test_soft_candy_env.py python/train/test_train_sb3.py tools/test_create_rl_curriculum_plan.py tools/test_create_rl_fixed_window_action_plan.py`
  - Result: `69 passed, 4 skipped`
- `env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run python python/train/train_sb3.py --dry-run --algorithm ppo --reward-profile terminal-sequence-recovery --steps 3 --train-maps caramel-workshop --train-map-selection cycle --train-seconds 300 --eval-seconds 1 --map-id caramel-workshop`
  - Result: dry-run returned `status=ok` and `reward_profile=terminal-sequence-recovery`

## Next Probe

Use this profile only as training evidence. A candidate still needs:

- guarded PPO or equivalent closed-loop probe on `caramel-workshop`
- high-pressure `60s / 180s / 300s` no-regression against the per-map edge branch + all-map late filter baseline
- terminal conversion probe gate proving online win-rate / survival improvement
- failure case and progress updates for any regression or no-conversion outcome

## Limitations

- No policy checkpoint was trained in this boundary.
- No online terminal conversion improvement is claimed yet.
- The profile does not relax RL acceptance, no-regression, Replay, or manual playtest requirements.
