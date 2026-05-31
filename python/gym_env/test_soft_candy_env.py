from python.gym_env.soft_candy_env import SoftCandyStormEnv


class PickSecondUpgrade:
    def choose(self, observation, upgrade_options):
        return {
            "choice_index": 1,
            "choice_upgrade_id": upgrade_options[1],
            "policy_kind": "fixture",
            "observation_len": len(observation),
        }


def test_pending_upgrade_prompt_uses_pluggable_policy():
    env = SoftCandyStormEnv.__new__(SoftCandyStormEnv)
    env.upgrade_policy = PickSecondUpgrade()
    env.last_observation = [0.1, 0.2, 0.3]
    env.last_info = {"upgrade_options": ["bubble-shoes", "cream-clockwork"]}

    decision = env._upgrade_choice_for_pending_prompt()

    assert decision["choice_index"] == 1
    assert decision["choice_upgrade_id"] == "cream-clockwork"
    assert decision["observation_len"] == 3


def test_no_pending_upgrade_prompt_omits_policy_decision():
    env = SoftCandyStormEnv.__new__(SoftCandyStormEnv)
    env.upgrade_policy = PickSecondUpgrade()
    env.last_observation = [0.1, 0.2, 0.3]
    env.last_info = {"upgrade_options": []}

    assert env._upgrade_choice_for_pending_prompt() is None


def test_seed_selector_cycles_training_seed_values():
    env = SoftCandyStormEnv.__new__(SoftCandyStormEnv)
    env.seed_value = 999
    env.seed_values = [62400, 62401]
    env.seed_selection = "cycle"
    env.seed_episode_index = 0

    assert env._select_seed_value() == 62400
    assert env._select_seed_value() == 62401
    assert env._select_seed_value() == 62400


def test_seed_selector_rejects_empty_seed_values():
    env = SoftCandyStormEnv.__new__(SoftCandyStormEnv)

    try:
        env._normalize_seed_values([])
    except ValueError as exc:
        assert "seed_values" in str(exc)
    else:
        raise AssertionError("expected empty seed values to be rejected")


def test_reward_profile_accepts_repair_profiles():
    env = SoftCandyStormEnv.__new__(SoftCandyStormEnv)

    assert env._normalize_reward_profile("late-survival") == "late-survival"
    assert env._normalize_reward_profile("long-run-retention") == "long-run-retention"
    assert env._normalize_reward_profile("mid-path-retention") == "mid-path-retention"
    assert (
        env._normalize_reward_profile("opening-mid-boundary-retention")
        == "opening-mid-boundary-retention"
    )
    assert env._normalize_reward_profile("late-route-recovery") == "late-route-recovery"
    assert env._normalize_reward_profile("late-win-conversion") == "late-win-conversion"
    assert (
        env._normalize_reward_profile("terminal-sequence-recovery")
        == "terminal-sequence-recovery"
    )
    assert env._normalize_reward_profile("opening-route-recovery") == "opening-route-recovery"
    assert env._normalize_reward_profile("opening-boundary-escape") == "opening-boundary-escape"
    assert env._normalize_reward_profile(None) == "standard"


def test_reward_profile_rejects_unknown_value():
    env = SoftCandyStormEnv.__new__(SoftCandyStormEnv)

    try:
        env._normalize_reward_profile("late_survival")
    except ValueError as exc:
        assert "reward_profile" in str(exc)
    else:
        raise AssertionError("expected unknown reward profile to be rejected")
