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
