# RL Training Entry Points

This folder contains the first Stable-Baselines3 training entry point for the Python Gym bridge.

The current bridge is Phase 1 only:

- 9 discrete movement actions.
- Headless `GameCore` through `game_harness gym-bridge`.
- Observation v2 with player stat modifiers, enemy relative velocity/radius/elite/behavior features, active hazard direction, boss summary, map dimensions, and corner proximity.
- Upgrade choices handled by the bridge rule policy.
- DQN/PPO config is intentionally small for smoke runs.

## Dependency Check

```bash
python3 python/train/train_sb3.py --check-deps
```

Real training requires:

```bash
python3 -m pip install -r python/train/requirements.txt
```

## Dry Run

```bash
python3 python/train/train_sb3.py --dry-run --algorithm dqn --steps 90
```

Dry-run validates the config and bridge without importing Stable-Baselines3.

## Real Training

```bash
python3 python/train/train_sb3.py --algorithm dqn
python3 python/train/train_sb3.py --algorithm ppo
```

For a minimal smoke, override the training and evaluation size:

```bash
python3 python/train/train_sb3.py --algorithm dqn --timesteps 128 --eval-episodes 2 --eval-seconds 5 --report harness/reports/local_rl_training/dqn_training_smoke.json
```

Use `--model-out <path>` and `--report-dir <path>` for experiments that should not overwrite the default per-algorithm model or local training reports.

`train_sb3.py` writes the model zip, per-algorithm model metadata, a training report, an evaluation report, and known exploit notes. Do not record RL Bot training as complete until all of those files exist and the policy has been compared against rule Bot baselines.

The shared config uses `observation_version: 2` and `observation_len: 145`. Older v1 models with 82 inputs can still be inspected by using a separate config that sets `observation_version: 1` and `observation_len: 82`; do not mix v1 models with v2 evaluation reports.

For multi-map training experiments, pass a comma-separated map list. `cycle` is deterministic and rotates maps on each environment reset; `random` uses the episode seed and episode index to select maps deterministically.

```bash
python3 python/train/train_sb3.py --algorithm ppo --train-maps frosting-grassland,soda-creek,caramel-workshop --train-map-selection cycle
```

Use `--train-map-preset` for common `base_demo` sets:

- `all-base-demo`: all six current maps.
- `high-pressure`: `soda-creek`, `caramel-workshop`, `cracked-star-jar`.
- `stable-open`: `frosting-grassland`, `cotton-cloud-pasture`, `jelly-platform`.

Use `--train-seconds` to change training episode length without changing evaluation length. This is useful after a policy passes short action-distribution checks but fails 300-second cross-map generalization.

```bash
python3 python/train/train_sb3.py --algorithm ppo --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

In training mode, pass `--map-id <id>` to choose the post-training evaluation map. This keeps short action-gate checks aligned with focused high-pressure or curriculum experiments instead of always falling back to the config default map.

```bash
python3 python/train/train_sb3.py --algorithm ppo --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60 --map-id soda-creek
```

Use `--model-in <path>` to continue training from a saved SB3 model and write the continued policy to `--model-out <path>`. Warm-start runs load adjacent `*_metadata.json` when available so reports can preserve the source model parameters. Algorithm override flags such as `--ent-coef` are intentionally blocked with `--model-in` until the runner can safely update loaded SB3 schedules.

```bash
python3 python/train/train_sb3.py --algorithm ppo --model-in python/train/models/ppo_phase1_observation_v2_high_pressure_train300_random_ent002_50000_eval60.zip --timesteps 20000 --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --model-out python/train/models/ppo_phase1_warm_start_example.zip
```

For PPO exploration experiments, use `--ent-coef <value>` to override the entropy coefficient without editing the shared config. Training metadata and reports record the final SB3 algorithm parameters.

```bash
python3 python/train/train_sb3.py --algorithm ppo --ent-coef 0.02 --train-maps frosting-grassland,soda-creek,caramel-workshop --train-map-selection random
```

## Policy vs Rule Bot Comparison

Compare a saved SB3 policy against rule Bot baselines with the same map, seed range, and duration:

```bash
python3 python/train/train_sb3.py --algorithm dqn --compare-rule-bots --model python/train/models/dqn_phase1_movement_survival.zip --seed-start 30000 --eval-episodes 2 --eval-seconds 5 --map-id frosting-grassland --rule-bots random,kite,tank --report harness/reports/local_rl_training/dqn_rule_bot_comparison.json
```

Use `--compare-map-preset` to run the same comparison over a preset map set and write one aggregate report:

```bash
python3 python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model python/train/models/ppo_phase1_observation_v2_multimap_random_ent002_50000_eval60.zip --seed-start 30000 --eval-episodes 10 --eval-seconds 300 --rule-bots random,kite,tank --report harness/reports/local_rl_training/ppo_high_pressure_comparison.json
```

The comparison report records the policy summary, action distribution, rule Bot matrix output, smoke findings, limitations, and `comparison_recorded_not_balance_gate` gate decision.

Multi-map comparison reports additionally include per-map policy/rule Bot win rates, dominant action, normalized action entropy, `repair_maps`, and a `multimap_comparison_*` gate decision. A multi-map report can mark `repair` even when per-map action distribution is healthy, because 0% win-rate maps still mean the policy is not ready as a cross-map RL test Bot.

Policy evaluation reports include `action_entropy_bits`, `normalized_action_entropy`, and averaged `reward_breakdown` fields so action collapse and reward-shaping issues can be inspected before treating a policy as a useful test Bot. The current Gym reward breakdown includes the safety shaping fields `low_health`, `boundary_risk`, `enemy_pressure`, `hazard_risk`, `boss_pressure`, and `safety_delta`. `safety_delta` rewards aggregate risk reduction between consecutive snapshots and penalizes rising risk, while the static safety fields remain lightweight diagnostics.

Evaluation reports also include `action_score_diagnostic`. For probability policies such as PPO, it records the mean action probabilities, top mean-probability actions, and how often each action was the policy's highest-probability action. For value policies such as DQN, it records the same aggregate view over q-values. Use this field when deterministic argmax keeps choosing one action even though sampled evaluation appears healthy.

Evaluation defaults to deterministic policy actions. Use `--eval-stochastic` with training, `--evaluate-model`, or `--compare-rule-bots` when diagnosing whether a policy still has useful action probability mass even though deterministic argmax collapses.

Training reports use `trained_needs_action_bias_repair` when the policy collapses to a dominant action or very low normalized action entropy; comparison reports use `comparison_recorded_needs_action_bias_repair` for the same condition.

## Rule Bot Trajectory Export

Use the Harness trajectory exporter to produce JSONL movement datasets from rule Bots before behavior cloning or policy distillation experiments:

```bash
cargo run -p game_harness -- export-bot-trajectories --bot kite --seed-start 30000 --seeds 10 --map-id soda-creek --seconds 300 --observation-version 2 --out harness/reports/local_bot_trajectories/kite_soda.jsonl
```

The first record is `metadata`, each `sample` contains an observation vector and discrete movement action, and the final record is `summary`. Upgrade-choice states are skipped because Phase 1 RL still trains movement only.

Use `--sample-start-seconds` and `--sample-end-seconds` to export only a time window while still simulating the full run. This is useful for collecting 300-second middle/late-game states without over-weighting the opening:

```bash
cargo run -p game_harness -- export-bot-trajectories \
  --bot kite \
  --seed-start 34000 \
  --seeds 5 \
  --map-id soda-creek \
  --seconds 300 \
  --sample-stride 10 \
  --sample-start-seconds 60 \
  --out harness/reports/local_bot_trajectories/kite_soda_late.jsonl
```

## Behavior Cloning Smoke

Use `train_behavior_clone.py` to train a small supervised movement clone from exported rule Bot trajectories:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001 \
  --epochs 2 \
  --batch-size 128 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_high_pressure_smoke_001/run_output.json
```

This entry point is for policy distillation and curriculum experiments only. A cloned model must still be wrapped for Gym evaluation, compared against rule Bot baselines, and reviewed for action bias before it can become an RL test Bot candidate.

Repeat `--dataset` to combine complementary trajectory windows, such as an opening dataset plus a 60-300 second lategame dataset:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --epochs 20 \
  --batch-size 256
```

Evaluate or compare a behavior clone checkpoint through the shared Gym policy diagnostics with `--behavior-clone-model`:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --eval-episodes 2 \
  --eval-seconds 10 \
  --map-id soda-creek \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_eval_smoke_001/comparison.json
```

The adapter exposes action probabilities to the existing `action_score_diagnostic` report, so deterministic collapse and low entropy are visible in the same format as SB3 policies.

Use `--class-weighting inverse_frequency` to run a quick loss-weighted repair attempt when exported trajectories are action-imbalanced:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001 \
  --epochs 20 \
  --batch-size 128 \
  --class-weighting inverse_frequency \
  --model-out python/train/models/behavior_clone_kite_high_pressure_weighted_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_weighted_smoke_001/run_output.json
```

The first weighted smoke improved offline validation accuracy but still collapsed deterministically to action `5` in Gym comparison, so class weighting is a diagnostic knob rather than a proven fix.

Use `--sample-weighting danger` to revisit low-health and lategame samples more often during training:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --sample-weighting danger \
  --epochs 20
```

This uses weighted sampling from the same multi-map dataset, so it should be validated with the normal Gym comparison reports before being treated as a repair.

The first danger-weighted run used the expanded, lategame, and cracked-star-jar targeted datasets. It kept 60-second high-pressure comparison healthy across all three maps, but the 300-second comparison still underperformed KiteBot on `cracked-star-jar`:

- 60 seconds: all three maps reached 100% win rate with normalized action entropy above 0.86.
- 300 seconds: average win rate improved to 55.56%, but `cracked-star-jar` remained 33.33% while KiteBot reached 100%.

Treat this as a `watch` result, not a policy gate pass. The next repair should add sequence context or staged policies rather than more single-map samples.

The first useful repair came from expanding the trajectory coverage rather than only changing loss weights:

```bash
cargo run -q -p game_harness -- export-bot-trajectories --bot kite --seed-start 31000 --seeds 5 --map-id soda-creek --seconds 60 --tick-rate 30 --observation-version 2 --sample-stride 5 --out harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001/kite_soda_creek.jsonl
```

Repeat the export for `caramel-workshop` and `cracked-star-jar`, then train:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --epochs 20 \
  --batch-size 256 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_expanded_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_expanded_smoke_001/run_output.json
```

The expanded smoke passed the short high-pressure comparison gate, but it is still only a 10-second smoke. Run longer 60/300-second comparisons before treating it as a useful distillation base.

The next lategame run combined the expanded opening dataset with a 60-300 second windowed dataset:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --epochs 20 \
  --batch-size 256 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_combined_lategame_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_combined_lategame_smoke_001/run_output.json
```

It improved the 300-second high-pressure average win rate to 22.22%, but `cracked-star-jar` remained at 0%, so the policy still needs repair.
