# RL Training Entry Points

This folder contains the first Stable-Baselines3 training entry point for the Python Gym bridge.

The current bridge is Phase 1 only:

- 9 discrete movement actions.
- Headless `GameCore` through `game_harness gym-bridge`.
- Observation v2 with player stat modifiers, enemy relative velocity/radius/elite/behavior features, active hazard direction, boss summary, map dimensions, and corner proximity.
- Upgrade choices default to the bridge's first-option fallback, but training/evaluation/comparison can pass an optional supervised upgrade-choice ranker.
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

Use `--reward-profile late-survival` for closed-loop late-window survival repair experiments. This profile is applied inside the Rust `gym-bridge`: after 180 seconds it ramps up survival, safety-risk reduction, low-health, boundary, enemy, hazard, boss-pressure, and terminal survival rewards/penalties. Use `--reward-profile long-run-retention` when a late-window repair regresses 60-180 second retention or collapses into repeated actions; it starts ramping after 60 seconds and also amplifies the repeated-action penalty. Use `--reward-profile late-win-conversion` when the policy reaches late windows but fails to convert 240-300 second states into victories; it ramps only in the final minute and gives a stronger terminal win/loss signal. These profiles are training evidence only; deterministic high-pressure 60/180/300-second gates are still required before any RL test Bot candidate review.

```bash
python3 python/train/train_sb3.py --algorithm ppo --reward-profile late-survival --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

```bash
python3 python/train/train_sb3.py --algorithm ppo --reward-profile long-run-retention --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

```bash
python3 python/train/train_sb3.py --algorithm ppo --reward-profile late-win-conversion --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

In training mode, pass `--map-id <id>` to choose the post-training evaluation map. This keeps short action-gate checks aligned with focused high-pressure or curriculum experiments instead of always falling back to the config default map.

```bash
python3 python/train/train_sb3.py --algorithm ppo --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60 --map-id soda-creek
```

Use `--model-in <path>` to continue training from a saved SB3 model and write the continued policy to `--model-out <path>`. Warm-start runs load adjacent `*_metadata.json` when available so reports can preserve the source model parameters. Algorithm override flags such as `--ent-coef` and `--learning-rate` are recorded in metadata and reports when used with `--model-in`; learning-rate overrides refresh the loaded SB3 schedule before training continues.

```bash
python3 python/train/train_sb3.py --algorithm ppo --model-in python/train/models/ppo_phase1_observation_v2_high_pressure_train300_random_ent002_50000_eval60.zip --timesteps 20000 --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --model-out python/train/models/ppo_phase1_warm_start_example.zip
```

For PPO exploration experiments, use `--ent-coef <value>` to override the entropy coefficient without editing the shared config. Use `--learning-rate <value>` when a repair run needs a smaller or larger optimizer step while preserving the shared config. Training metadata and reports record the final SB3 algorithm parameters.

```bash
python3 python/train/train_sb3.py --algorithm ppo --ent-coef 0.02 --train-maps frosting-grassland,soda-creek,caramel-workshop --train-map-selection random
```

For curriculum retention experiments, use `--train-seeds <a,b,c>` or `--train-seed-start <N> --train-seed-count <M>` to replay known regression seeds during training resets. Training reports record the seed set and selection mode, while `--seed-start` remains reserved for evaluation and rule Bot comparison:

```bash
python3 python/train/train_sb3.py --algorithm ppo --model-in harness/reports/local_stage01/stage01.zip --train-maps soda-creek,caramel-workshop --train-map-selection random --train-seed-start 62400 --train-seed-count 10 --train-seed-selection cycle
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

Policy evaluation reports include `action_entropy_bits`, `normalized_action_entropy`, and averaged `reward_breakdown` fields so action collapse and reward-shaping issues can be inspected before treating a policy as a useful test Bot. The current Gym reward breakdown includes the safety shaping fields `low_health`, `boundary_risk`, `enemy_pressure`, `hazard_risk`, `boss_pressure`, `safety_delta`, `corner_action_risk`, `corner_risk_delta`, `opening_edge_risk_delta`, and `route_recovery`. `safety_delta` rewards aggregate risk reduction between consecutive snapshots and penalizes rising risk, while the static safety fields remain lightweight diagnostics. `corner_action_risk` is retained as a compatibility field for the earlier opening failure diagnostic; current opening repair uses `corner_risk_delta` and `opening_edge_risk_delta`, state-based rewards for lowering opening corner / edge pressure instead of penalizing a specific diagonal action. `route_recovery` is action-aware: movement toward the current recovery direction gets a small reward, while movement into boundary, enemy, hazard, or Boss pressure gets a small penalty; upgrade-choice frames keep it at zero. These fields are diagnostic / repair evidence rather than policy acceptance evidence until high-pressure multi-map gates pass.

Evaluation reports also include `action_score_diagnostic`. For probability policies such as PPO, it records the mean action probabilities, top mean-probability actions, and how often each action was the policy's highest-probability action. For value policies such as DQN, it records the same aggregate view over q-values. Use this field when deterministic argmax keeps choosing one action even though sampled evaluation appears healthy.

Evaluation defaults to deterministic policy actions. Use `--eval-stochastic` with training, `--evaluate-model`, or `--compare-rule-bots` when diagnosing whether a policy still has useful action probability mass even though deterministic argmax collapses. Add `--eval-random-seed <N>` with `--eval-stochastic` to make sampled action selection reproducible; reports record `action_random_seed` and the seeded random sources. Seeded stochastic evaluation is diagnostic evidence only and does not replace deterministic high-pressure gates or RL policy acceptance.

Use `--opening-model <zip> --opening-seconds <seconds>` with `--evaluate-model` or `--compare-rule-bots` to test a staged policy that uses a known SB3 opening checkpoint before falling back to `--model` or `--behavior-clone-model`. This is evaluation-only evidence for split-policy repair; it does not train a new checkpoint or count as policy acceptance by itself.

Use `--edge-recovery-filter` with `--evaluate-model` or `--compare-rule-bots` to run a deterministic diagnostic wrapper that replaces a wall-pushing action with the highest-scoring action that does not keep pushing into a nearby map edge. Reports include `policy_adapter.mode = edge_recovery_filter`. This is only handoff repair evidence; the RL acceptance validator rejects policy-adapter reports.

Behavior clone repair experiments can load `edge_recovery_supervision_sample` rows and upweight them with `--edge-recovery-sample-weight`. Use `--edge-recovery-min-seconds` and `--edge-recovery-max-seconds` to keep those repair rows inside a handoff or mid-window while leaving normal rule Bot trajectory samples untouched. This is meant to prevent edge recovery samples from contaminating an opening submodel when a staged clone is trained.

Use `--sample-path-weight PATH=WEIGHT` when a mixed behavior-clone dataset needs source-specific sampling weight. `PATH` may be an exact JSONL path or a directory prefix; matching samples are multiplied after the normal danger/action/phase/recovery weights and are reported under `sample_weights.sample_path_weights`. This is useful when repair samples, clean survival anchors, or map-specific traces need different strengths without duplicating JSONL files. It is still supervised sampling evidence only and must be followed by fixed-window no-regression checks.

Use `--recovery-soft-target top_k_scores` when recovery samples should express a small action distribution instead of a single hard repair action. The target action receives `--recovery-soft-target-primary-mass`, and the remaining mass is spread across non-original `action_scores.top_actions` up to `--recovery-soft-target-top-k`. This is meant for route-recovery repair samples where hard labels can move deterministic policies from one dominant action to another; it is still training input only, not policy acceptance evidence.

The first handoff-window staged GRU context8 candidate used `--edge-recovery-min-seconds 60 --edge-recovery-max-seconds 180` with the stage01 opening wrapper. It preserved the 60-second high-pressure opening gate and closed the 180-second seed `62201` handoff failures, but the 300-second high-pressure probe still failed in the `late_180_to_300` bucket across all maps. Treat the result as late-window repair evidence, not stage 03 or RL acceptance.

Use `tools/validate_policy_window_regression.py` after any staged or closed-loop repair probe to compare it against the current baseline on the same fixed windows. Provide matching `LABEL=PATH` pairs for baseline and candidate reports, for example `60s=.../comparison_60s.json`, `180s=.../comparison_180s.json`, and `300s=.../comparison_300s.json`. A passing result only means no regression against that baseline; it is not RL acceptance and does not replace the acceptance manifest. When a probe continues from a limited-followup parent, feed both the original baseline and the parent-preservation report into `tools/validate_rl_repair_probe_gate.py` with `--required-window-regression e30=...` and `--required-window-regression parent=...`; a parent regression must block the branch even if the older baseline still passes.

The failed-only late trace shows the next repair should be broader than wall recovery: 7 / 8 terminal frames are still edge-pinned, but 5 / 8 also include hazard pressure and 5 / 8 include boss pressure. Late-window experiments should combine edge escape, hazard avoidance, boss pressure, and low-health recovery before re-running the 300-second gate.

Use `--late-recovery-filter` with evaluation or rule-Bot comparison to emit deterministic late-window repair decisions after `--late-recovery-min-seconds` (default 180s). The filter can redirect wallward edge actions, hazard-facing movement, boss/enemy pressure movement, and idle actions under late pressure. When paired with `--edge-recovery-samples-out`, these decisions are written as `risk_recovery_supervision_sample` rows. Behavior clone experiments can load those rows as movement repair targets, upweight them with `--risk-recovery-sample-weight`, and keep them in a late window with `--risk-recovery-min-seconds` / `--risk-recovery-max-seconds`. This is training material only; it remains policy-adapter evidence and does not satisfy stage 03 or RL acceptance.

Before mixing late-risk samples into behavior clone training, validate them:

```bash
python3 tools/validate_risk_recovery_samples.py harness/reports/local_late_recovery/*.jsonl --report harness/reports/local_late_recovery/risk_recovery_samples_validation.json
```

The validator checks sample role, target source, observation shape, late-window timing, adapter risk reasons, target residual risk, and acceptance-evidence wording. A valid report only means the rows are usable as repair training input; it does not upgrade adapter probes into policy gates.

When a validation report shows target residual-risk warnings, export a clean subset before a focused ablation:

```bash
python3 tools/filter_risk_recovery_samples.py harness/reports/local_late_recovery/*.jsonl --out harness/reports/local_late_recovery/risk_recovery_samples_clean.jsonl --report harness/reports/local_late_recovery/filter_report.json
```

The clean subset removes invalid rows, rows whose target action still has adapter target-risk reasons, and rows whose continuous target risk score is worse than the original action. It is still adapter-derived repair data, so train it with low weight / ablation discipline and rerun deterministic 60 / 180 / 300 second high-pressure gates.

Training reports use `trained_needs_action_bias_repair` when the policy collapses to a dominant action or very low normalized action entropy; comparison reports use `comparison_recorded_needs_action_bias_repair` for the same condition.

## Policy Acceptance Gate

Use `rl_policy_acceptance_template.json` as the manifest shape for deciding whether a trained policy can become an RL test Bot candidate:

```bash
python3 tools/validate_rl_policy_acceptance.py \
  python/train/rl_policy_acceptance_template.json \
  --repo-root . \
  --report harness/reports/local_rl_policy_acceptance/rl_policy_acceptance.json \
  --markdown harness/reports/local_rl_policy_acceptance/summary.md
```

The validator requires a model artifact, training report, local binary diagnostic, 60-second high-pressure comparison, 300-second high-pressure comparison, rule Bot comparison, and unresolved failure-case review before `gate_decision` may be `rl_test_bot_candidate`. It rejects release/playtest/balance wording because RL policy acceptance is only a testing-tool gate.

The current template is intentionally `blocked_by_local_binary_launch`: the context3 danger-weighted behavior clone trained successfully, but Gym comparison was blocked by the local Mach-O launch policy and therefore cannot be promoted.

## Rule Bot Trajectory Export

Use the Harness trajectory exporter to produce JSONL movement datasets from rule Bots before behavior cloning or policy distillation experiments:

```bash
cargo run -p game_harness -- export-bot-trajectories --bot kite --seed-start 30000 --seeds 10 --map-id soda-creek --seconds 300 --observation-version 2 --out harness/reports/local_bot_trajectories/kite_soda.jsonl
```

The first record is `metadata`, each `sample` contains an observation vector and discrete movement action, and the final record is `summary`. Upgrade-choice states are skipped by default because Phase 1 RL still trains movement only.

Use `--include-upgrade-samples true` when a run should also emit upgrade-choice supervision records. This keeps normal movement `sample` records unchanged and adds `upgrade_sample` records at upgrade prompts:

```bash
cargo run -p game_harness -- export-bot-trajectories \
  --bot kite \
  --seed-start 56000 \
  --seeds 2 \
  --map-id soda-creek \
  --seconds 60 \
  --observation-version 2 \
  --sample-stride 15 \
  --include-upgrade-samples true \
  --out harness/reports/local_bot_trajectories/kite_soda_upgrade_samples.jsonl
```

`load_trajectory_dataset` skips `upgrade_sample` records and reports their count as `upgrade_sample_records`. Use `load_upgrade_choice_dataset` and `summarize_upgrade_choice_dataset` to inspect upgrade supervision separately; this path is dataset plumbing only, not an RL policy gate.

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

Use `--context-frames <N>` to concatenate recent observations from the same exported episode before the MLP classifier. The default is `1` and remains compatible with older checkpoints. Context checkpoints record `base_observation_len`, `input_observation_len`, and `context_frames`; the Gym adapter resets the cached context at each evaluation episode boundary.

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --context-frames 3 \
  --sample-weighting danger \
  --epochs 20
```

The first `--context-frames 3` danger-weighted model trained successfully with `input_observation_len = 435` and 86.87% validation accuracy. After Developer Mode / Developer Tool permissions were restored, the local binary diagnostic returned `local_binary_launch_ok`, `game_harness --help` launched, `cargo test --workspace` passed, and Gym comparisons could run again.

The current high-pressure recheck keeps the checkpoint in `repair`: the 60-second `seed-start 42000` comparison reached 100% win rate on all three maps with healthy action entropy, but the 300-second `seed-start 43000` comparison still recorded 0% win rate on `caramel-workshop`. An alternate `seed-start 45000` window moved the weakness to `soda-creek` and `cracked-star-jar`, so this is a policy generalization issue rather than a host launch issue.

To move beyond flat MLP context windows, train a recurrent clone with `--architecture gru`. The GRU path keeps `--context-frames` as a sequence, supports `--map-conditioning one_hot`, and produces checkpoints that can be evaluated by the same `train_sb3.py --behavior-clone-model` comparison flow:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --architecture gru \
  --context-frames 8 \
  --map-conditioning one_hot \
  --sample-weighting danger
```

The first context8 map-conditioned GRU smoke proved the training and evaluation path, but it is not a policy repair: 60-second high-pressure comparison reached only 80% win rate on all three maps, and 300-second comparison reached 0% on all three maps. Treat it as a `repair` failure case before trying larger GRU runs.

Before expanding a recurrent run, use behavior clone dry-run reports as sequence diagnostics. Dry-run now records context padding, sequence span, action persistence, late low-health coverage, and per-map action distributions, so GRU failures can be separated into data coverage issues versus architecture or loss issues:

```bash
python3 python/train/train_behavior_clone.py \
  --dry-run \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_cracked_lategame_001 \
  --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_caramel_recovery_001 \
  --architecture gru \
  --context-frames 8 \
  --map-conditioning one_hot \
  --report harness/reports/local_rl_sequence_diagnostic/run_output.json
```

Treat `high_context_padding`, `high_action_persistence`, `low_late_low_health_coverage`, or `map_sample_imbalance` as `watch` signals that should be explained before another long GRU training run.

When deterministic policies become overconfident, use `--entropy-regularization <weight>` as a small confidence-penalty experiment. The training objective subtracts mean policy entropy from cross entropy, while the report keeps both `train_loss` and `train_cross_entropy_loss` so the regularized objective cannot be confused with plain imitation accuracy:

```bash
python3 python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --architecture gru \
  --context-frames 8 \
  --map-conditioning one_hot \
  --entropy-regularization 0.02
```

This is only an action-distribution diagnostic knob. A checkpoint trained with entropy regularization still needs the normal 60/300 second high-pressure comparison and RL policy acceptance review.

The first full `--entropy-regularization 0.02` GRU context8 run trained on the same expanded, lategame, cracked lategame, and caramel recovery trajectories. Offline validation accuracy stayed at `87.84%`, and 60-second high-pressure comparison improved `caramel-workshop` to 100%, but the 300-second comparison still recorded 0% win rate on `soda-creek` and `cracked-star-jar` with a `repair` gate. Treat entropy regularization as useful diagnostics for action spread, not as the long-window policy repair.

Use `--time-phase-conditioning one_hot` to append normalized run-progress phase features to behavior clone inputs. The default thresholds split the observation's time-progress value into opening, mid, and late phases at `0.2` and `0.6`; online evaluation computes the same features from the current Gym observation, so old checkpoints remain compatible while staged-policy experiments can make phase evidence explicit:

```bash
python3 python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --architecture gru \
  --context-frames 8 \
  --map-conditioning one_hot \
  --time-phase-conditioning one_hot
```

The first dry-run on the current high-pressure trajectory set found `opening` / `mid` / `late` ratios of `4.92%` / `42.51%` / `52.56%`. This only proves feature plumbing and dataset visibility; it is not policy repair until a checkpoint passes the same high-pressure comparison and acceptance gate.

Use `--sample-weighting time_phase_balance` when those progress buckets are badly imbalanced. It can be combined with the existing repair signals through `time_phase_balance_danger`, `time_phase_balance_action_change`, or `time_phase_balance_danger_action_change`; training reports include per-phase multipliers so the curriculum stays auditable.

The first `time_phase_balance_danger_action_change` smoke used the phase-aligned high-pressure dataset and trained a 1 epoch GRU context8 checkpoint. It recorded phase multipliers of `1.355244` / `0.728488` / `1.124329` for opening / mid / late, then loaded through a 5-second `soda-creek` Gym evaluation. Treat this as curriculum plumbing only; it is not a long-run policy repair.

The full `time_phase_balance_danger_action_change` GRU context8 candidate trained for 20 epochs and passed the 60-second high-pressure comparison without findings. The 300-second comparison still failed with 0% win rate on `soda-creek` and 33.33% on `caramel-workshop` / `cracked-star-jar`, even though action entropy stayed healthy. Treat this as movement-policy repair evidence: phase-balanced sampling helps action spread, but does not solve long-run objectives by itself.

Distilling that teacher into an SB3 PPO zip with `--teacher-temperature 1.5 --uniform-target-mix 0.05` produced a loadable initialization, but deterministic 10-second `soda-creek` evaluation collapsed back to action `3` at 100%. Use this only as a serialization smoke; PPO closed-loop training or stronger target entropy must come next.

The first 10k timestep PPO closed-loop run from that distilled zip used high-pressure random map sampling, 300-second train episodes, and `ent_coef=0.02`. It passed the 60-second high-pressure comparison, but failed the 300-second comparison with 0% win rate on `soda-creek` and `caramel-workshop`. Treat this as evidence that short warm-start PPO can reduce collapse but still needs long-run curriculum, reward targets, or movement + upgrade joint training.

Use `tools/analyze_rl_policy_failures.py <comparison.json>` after failed multimap comparisons to bucket defeated episodes by time window and map. The first analysis of the 10k closed-loop PPO report showed `soda-creek` failures skewing toward opening deaths while `caramel-workshop` failures skewed toward late 180-300 second deaths, which should drive separate curriculum fixes.

Use `tools/create_rl_curriculum_plan.py <failure_analysis.json>` to turn those failure buckets into a staged PPO curriculum manifest. The first plan starts from the 10k time-phase PPO model and creates chained opening, mid, and late stages with generated train/compare commands. It is a planning artifact only: each stage still needs to be trained, compared against rule Bots, and recorded as watch/repair/failure evidence before it can affect RL policy acceptance.

The first stage 01 opening run trained for 5120 actual timesteps on `cracked-star-jar` and `soda-creek`, then ran the planned 60-second high-pressure comparison. It reached 100% win rate on `caramel-workshop` and `cracked-star-jar`, but `soda-creek` stayed at 66.67% with one opening death at 29.1666 seconds. Treat this as repair evidence only; do not chain later curriculum stages as if opening survival has passed.

Continuing stage 01 for 20k more requested timesteps improved the 10-seed 60-second check but still did not pass: `soda-creek` reached 80% while `caramel-workshop` and `cracked-star-jar` stayed at 100%. The remaining `soda-creek` failures died at 46.1996s and 28.8332s with action `4` dominating the failed episodes, so the next repair should inspect opening trajectories and map pressure instead of only adding generic PPO timesteps.

Use `--trace-dir` to write sampled policy episode traces during training evaluation, `--evaluate-model`, or `--compare-rule-bots`. Combine it with `--trace-failed-only` to keep only non-victory episodes, and tune `--trace-sample-stride` to control row density:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --algorithm ppo \
  --evaluate-model \
  --model harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip \
  --eval-episodes 4 \
  --eval-seconds 60 \
  --seed-start 62406 \
  --map-id soda-creek \
  --trace-dir harness/reports/local_rl_trace/traces \
  --trace-failed-only \
  --trace-sample-stride 30 \
  --report harness/reports/local_rl_trace/evaluation.json
```

The first stage 01 retry trace confirmed that the two failed `soda-creek` episodes were not random jitter: both sustained action `4` at high policy probability through the final health collapse. Trace files are sampled from Gym evaluation info and do not replace Replay or full GameCore snapshots; use them for action/reward/health diagnostics, then add richer snapshot fields if map pressure remains ambiguous.

Trace rows now include `diagnostics` from the Gym bridge: player position and velocity, map size, boundary distances, nearest enemy, nearby enemy counts, and positive risk scores for low health, enemy pressure, hazards, bosses, and overall safety. The first snapshot trace showed both failed `soda-creek` seeds pinned at the bottom-right map edge with `boundary.min_distance = 0`, `enemy_pressure_risk = 1`, and direct enemy contact, while action `4` remained the chosen policy action.

A follow-up snapshot comparison traced both failed and successful seeds from the same four-episode window. It showed that all episodes touch map boundaries; the actionable difference is that successful seeds eventually reverse to action `7` and shed enemy pressure, while failed seeds keep a long action `4` tail at the right/bottom corner.

The Gym reward breakdown now includes `corner_action_risk` for that specific opening failure mode. A diagnostic rerun of the unchanged stage 01 retry policy on `soda-creek` seeds `62406` to `62409` recorded average `corner_action_risk = -0.6767`; the failed seeds `62406` / `62409` ended with action `4` and final-frame `corner_action_risk = -0.006`, while the successful seeds ended on action `7` with no final corner penalty. Report: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_corner_reward_001/summary.md`. This is reward instrumentation only; the next valid repair step is to warm-start retrain and rerun the 60-second high-pressure 10 seed comparison.

The first 20k warm-start with `corner_action_risk` is a repair regression, not a fix. The training evaluation dropped `soda-creek` to 0% win rate and collapsed to action `8` at 92.90%; the same 60-second high-pressure 10 seed comparison recorded `soda-creek` / `caramel-workshop` / `cracked-star-jar` at 10% / 80% / 70% with action `8` dominant on every map. Report: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_retrain_20k_001/summary.md`; failure case: `harness/failed_cases/fail_20260527_020_corner_reward_retrain_action8_collapse.json`. Do not use that checkpoint for stage 02.

The directional `corner_action_risk` smoke penalizes any diagonal action that pushes into the currently pressured corner and lowers the penalty to `-0.003`. A 2048 timestep warm-start avoided the action `8` collapse, but the 60-second high-pressure 10 seed comparison still reached only 70% / 90% / 100% on `soda-creek` / `caramel-workshop` / `cracked-star-jar`, with 3 opening deaths left on `soda-creek`. Report: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_directional_smoke_001/summary.md`; failure case: `harness/failed_cases/fail_20260527_021_directional_corner_reward_smoke_soda_gap.json`. Treat it as smoke-only repair evidence.

The state-based `corner_risk_delta` smoke replaces action-specific shaping with pressure-risk delta in the opening corner state. A 2048 timestep warm-start reached 100% / 100% / 100% on the 60-second high-pressure 10 seed deterministic comparison and also passed stochastic sampling on the same maps and seeds. Report: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/summary.md`. Treat it as stage 01 opening repair evidence that can start stage 02 mid-window experiments, not as full RL policy acceptance.

The first stage 02 mid-window continuation from that checkpoint is a repair regression. Training only on `caramel-workshop` for 180 seconds reached 100% on the target training evaluation, but the 180-second high-pressure three-map comparison dropped `soda-creek` to 33.33% and reopened one opening death; `caramel-workshop` also triggered action-bias repair with action `2` at 77.81%. Report: `harness/reports/2026-05-27_rl_curriculum_stage02_corner_risk_delta_mid_001/summary.md`; failure case: `harness/failed_cases/fail_20260527_022_stage02_corner_risk_delta_mid_regression.json`. Do not enter stage 03 from that checkpoint; stage 02 needs opening retention or mixed-seed regularization.

The first mixed-retention stage 02 attempt trains on `soda-creek` + `caramel-workshop`. It fixes the target-map action `2` collapse, but it still regresses the opening gate: `soda-creek` reaches only 80% on the 60-second high-pressure 10 seed regression and 66.67% on the 180-second three-map smoke. Report: `harness/reports/2026-05-27_rl_curriculum_stage02_mixed_retention_001/summary.md`; failure case: `harness/failed_cases/fail_20260527_023_stage02_mixed_retention_opening_regression.json`. Keep 60-second opening regression as a hard gate after every stage 02 update.

The low-learning-rate short stage 02 continuation tests `--learning-rate 0.0001` with only 1024 timesteps from the same stage 01 checkpoint. It still fails the hard opening gate: `soda-creek` remains at 80% in the 60-second high-pressure 10 seed regression, with seed 62400 dying earlier at 24.5666s. Report: `harness/reports/2026-05-27_rl_curriculum_stage02_low_lr_short_001/summary.md`; failure case: `harness/failed_cases/fail_20260527_024_stage02_low_lr_short_opening_regression.json`. Do not enter stage 03 from this checkpoint; the next repair needs explicit opening replay or regularization instead of another generic PPO continuation.

The first seed-replay stage 02 continuation trains with `--train-seed-start 62400 --train-seed-count 10` plus the low-learning-rate short setup. It improves `soda-creek` from 80% to 90% on the 60-second high-pressure 10 seed regression, but seed 62405 still dies at 47.3330s. Report: `harness/reports/2026-05-27_rl_curriculum_stage02_seed_replay_short_001/summary.md`; failure case: `harness/failed_cases/fail_20260527_025_stage02_seed_replay_short_opening_regression.json`. Keep this as repair evidence only; do not run stage 03 until the full opening gate passes.

The seed 62405 trace comparison shows the remaining regression more precisely. The stage 01 checkpoint survives by switching from action `4` to action `7` at the bottom-right corner under enemy pressure; the stage 02 seed-replay checkpoint instead moves to the top-right, follows action `4` down the right edge, and dies in the bottom-right corner without sampling action `7`. Report: `harness/reports/2026-05-27_rl_curriculum_stage02_seed62405_trace_compare_001/summary.md`. The next repair should target right-edge / bottom-right pressure states rather than only adding more replay seeds.

The first full time-phase-conditioned GRU context8 checkpoint kept healthy action entropy and improved the 60-second window to 100% / 80% / 100%, but the 300-second window still recorded 0% win rate on `soda-creek` and `caramel-workshop` and only 33.33% on `cracked-star-jar`. Treat this as another `repair` result: progress buckets are useful evidence, but they are not a replacement for phase-specific objectives, upgrade supervision, or PPO distillation.

For a true staged-policy experiment, train separate opening/mid/late behavior clones with `--time-phase-filter`, then package them with `create_staged_behavior_clone_policy.py`. By default, the staged checkpoint dispatches to the matching subpolicy at evaluation time based on the current observation's normalized time progress:

```bash
python3 python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --time-phase-filter opening \
  --model-out harness/reports/local_staged/opening.pt

python3 python/train/create_staged_behavior_clone_policy.py \
  --opening-model harness/reports/local_staged/opening.pt \
  --mid-model harness/reports/local_staged/mid.pt \
  --late-model harness/reports/local_staged/late.pt \
  --model-out harness/reports/local_staged/staged.pt
```

When a staged checkpoint is trained against a fixed long-run horizon, pass `--phase-duration-seconds 300` during packaging. Evaluation then dispatches phases from the absolute `time_seconds` supplied by the Gym loop, so a 60-second opening probe keeps using the opening subpolicy until 60s instead of treating 36s as `late` just because the short evaluation horizon has reached 60% progress. Old staged checkpoints without this field keep the normalized-time behavior for reproducibility.

The clean-teacher late survival candidate was repackaged with `--phase-duration-seconds 300` and rerun on deterministic high-pressure 60 / 180 / 300 second comparisons. The absolute-time package still recorded 70% / 100% / 80% at 60 seconds, 66.67% / 100% / 33.33% at 180 seconds, and 0% / 0% / 0% at 300 seconds. Treat absolute-time dispatch as correct packaging plumbing, not as a clean-teacher strategy fix.

To improve the weakest clean-teacher map coverage, an extra `caramel-workshop` TankBot scan found one additional 300-second victory at seed `62405`. Exporting its `180-300s` window added `719` clean trajectory samples and raised the clean-teacher `caramel-workshop` share from `11.76%` to `21.03%`. This is dataset coverage only; train a new late subpolicy and rerun the normal deterministic high-pressure comparisons before treating it as repair evidence.

The expanded clean-teacher late subpolicy improved offline validation accuracy from `0.7200` to `0.7633`, but deterministic high-pressure results did not improve: `70% / 100% / 80%` at 60 seconds, `66.67% / 100% / 33.33%` at 180 seconds, and `0% / 0% / 0%` at 300 seconds. Treat this as evidence that clean-teacher-only late replacement is exhausted unless the next attempt adds opening/mid retention, contrastive constraints, or closed-loop late survival objectives.

The late-risk + clean-teacher mix trained the late subpolicy from phase-aligned rule trajectories, expanded clean-teacher survival trajectories, edge recovery samples, and risk recovery samples. It reached `0.8025` validation accuracy and preserved the deterministic 180-second handoff comparison, but 300-second high-pressure still recorded `0% / 0% / 0%`; all failures were in `late_180_to_300`. Treat this as a handoff-preserving repair result, not a policy candidate.

The first packaging smoke proved the staged checkpoint can be loaded through the existing Gym comparison path, but the 1 epoch subpolicies still showed action-bias repair findings. Treat staged packaging as plumbing until a fully trained staged policy passes the normal acceptance gate.

The first full staged GRU context8 candidate trained separate opening, mid, and late subpolicies and packaged them with relative paths. It still failed earlier than the time-phase single model: the 60-second high-pressure comparison marked `soda-creek` as repair with 20% win rate and action 3 at 76.72%, and the 300-second comparison kept `soda-creek` at 0%. This confirms that staged dispatch alone is not enough; the next repair should add phase objectives, upgrade-choice supervision, broader opening data, or PPO distillation.

The phase-aligned staged retry exported fresh 300-second high-pressure trajectories so the `opening` filter covered 0-60 seconds instead of only the first 12 seconds of a 60-second episode. This raised opening samples from 1080 to 5388, but the policy still collapsed on `soda-creek`: 0% win rate in the 60-second comparison with action 3 at 79.11%, and 0% `soda-creek` plus 0% `caramel-workshop` in the 300-second comparison. Treat this as evidence that data-window alignment alone is not enough; the next repair needs phase objectives, upgrade-choice data, teacher soft targets, or PPO distillation.

The first useful repair came from expanding the trajectory coverage rather than only changing loss weights:

```bash
cargo run -q -p game_harness -- export-bot-trajectories --bot kite --seed-start 31000 --seeds 5 --map-id soda-creek --seconds 60 --tick-rate 30 --observation-version 2 --sample-stride 5 --out harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001/kite_soda_creek.jsonl
```

When `sequence_diagnostics` reports high action persistence, use `--sample-weighting action_change` or `--sample-weighting danger_action_change` to oversample action transition points inside each episode. This is a diagnostic/training knob only; it still needs the normal high-pressure comparison and acceptance manifest before a policy can move forward.

The first full `danger_action_change` staged GRU context8 candidate improved the short-window action distribution: 60-second `soda-creek` moved from 0% to 40% win rate, normalized entropy rose from 0.2356 to 0.6104, and dominant action ratio fell from 0.7911 to 0.5226. The 300-second comparison still recorded 0% win rate on all three high-pressure maps, so action-change weighting is a useful diagnostic repair but not a long-run policy fix.

`distill_behavior_clone_to_sb3.py` can now initialize an SB3 PPO `MlpPolicy` from behavior clone teacher probabilities:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/distill_behavior_clone_to_sb3.py \
  --dataset harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001 \
  --teacher-model harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt \
  --teacher-temperature 1.5 \
  --uniform-target-mix 0.05 \
  --model-out harness/reports/local_distillation/ppo_bc_distilled.zip \
  --report harness/reports/local_distillation/run_output.json
```

Use `--teacher-temperature` and `--uniform-target-mix` only as explicit repair experiments when the teacher probabilities are too sharp or action-biased. They raise target entropy before supervised PPO initialization, but the resulting `.zip` is still only an initialization/plumbing gate until followed by PPO training and high-pressure comparison.

When the useful teacher is an evaluation wrapper with a stronger SB3 opening policy and a behavior-clone fallback, pass `--opening-model <zip> --opening-seconds <seconds>` during distillation. The distiller forwards each dataset sample's `time_seconds` into the wrapper before reading teacher probabilities, so opening rows use the SB3 opening model and later rows use the fallback clone. This is still only initialization evidence; run fixed-window high-pressure comparisons before any policy gate claim.

When a supervised SB3 re-alignment needs the `anchor_drift_sample` rows exported by `export_anchor_drift_samples.py --include-observation`, pass `--include-anchor-drift-samples` to `distill_behavior_clone_to_sb3.py`. The flag is explicit so drift diagnostics do not silently become ordinary trajectory imitation data; use it only for repair initialization, then rerun anchor alignment and fixed-window no-regression.

Use repeated `--sample-path-weight PATH=WEIGHT` with `distill_behavior_clone_to_sb3.py` when a broad full-anchor dataset needs a small repair slice, such as `anchor_drift_sample` rows, to affect supervised SB3 initialization. Matching uses the same exact-path or directory-prefix semantics as behavior-clone training and is reported under `sample_weights`; it is still initialization evidence only.

Distillation reports include `validation_slices`, grouped by `sample_source` and by every configured `--sample-path-weight` match. Use these slice metrics to check whether a weighted repair source improved without hiding full-anchor regression behind the aggregate validation loss.

Use `compare_sb3_to_behavior_clone_anchor.py` after closed-loop PPO continuation when you need to measure how far a candidate drifted from a behavior-clone anchor. It reports KL divergence, argmax agreement, and per-map / per-time-bucket alignment over offline trajectory samples, and it can use the same `--opening-model <zip> --opening-seconds <seconds>` anchor wrapper. Passing thresholds in this report is only repair evidence; it does not replace high-pressure comparison or no-regression validation.

When comparing against `anchor_drift_sample` JSONL rows from `export_anchor_drift_samples.py --include-observation`, pass `--include-anchor-drift-samples`. The flag is explicit so drift diagnostics do not silently become normal behavior-clone data; use it for pre-checking a start model against selected high-KL rows before launching another guarded PPO continuation.

Use `--anchor-model` with repeated `--anchor-dataset` during PPO training when a closed-loop continuation must stay close to a behavior-clone anchor. The trainer runs PPO in chunks, then applies offline KL regularization on the anchor samples before the next chunk. Add `--anchor-opening-model` when the anchor should dispatch to an SB3 opening checkpoint before falling back to the behavior clone:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --algorithm ppo \
  --model-in harness/reports/local_probe/ppo_warm_start.zip \
  --reward-profile late-win-conversion \
  --train-map-preset high-pressure \
  --train-map-selection random \
  --train-seconds 300 \
  --timesteps 2048 \
  --anchor-model harness/reports/local_anchor/fallback.pt \
  --anchor-opening-model harness/reports/local_anchor/opening.zip \
  --anchor-dataset harness/reports/local_anchor/anchor_samples \
  --anchor-regularization-interval 512 \
  --anchor-regularization-weight 1.0 \
  --anchor-sample-weighting map_time_bucket_balance \
  --anchor-include-time-buckets opening_lt_60,mid_60_to_180,late_180_to_300 \
  --anchor-time-bucket-weights opening_lt_60=2.0,mid_60_to_180=1.0,late_180_to_300=1.25 \
  --anchor-guard-max-validation-kl 0.25 \
  --anchor-guard-min-argmax-agreement 0.85 \
  --model-out harness/reports/local_probe/ppo_anchor_constrained.zip
```

The training report records `anchor_regularization.final_validation.mean_kl` and `argmax_agreement`, plus per-chunk validation metrics. Use `--anchor-sample-weighting time_bucket_balance` when opening/mid/late samples are imbalanced, or `--anchor-sample-weighting map_time_bucket_balance` when a map and time bucket should not be diluted by the rest of the anchor dataset; the report records group counts and multipliers under `anchor_regularization.sample_weighting`. Use `--anchor-include-time-buckets` to constrain the KL objective to selected phases, and `--anchor-time-bucket-weights bucket=weight,...` to apply phase-specific multipliers after the normal balancing pass. `--anchor-dataset` can also read `anchor_drift_sample` JSONL rows produced with `export_anchor_drift_samples.py --include-observation`; those rows are accepted only inside anchor regularization and are treated as repair diagnostics, not normal behavior-clone imitation samples. `--anchor-guard-max-validation-kl` and `--anchor-guard-min-argmax-agreement` add an online anchor-drift guard: after each PPO chunk and KL repair epoch, the trainer records `validation_guard` and stops further chunks if the offline anchor validation exceeds the configured thresholds. This guard prevents a bad continuation from simply being trained longer, but it is still not a fixed-window no-regression report; a checkpoint still needs `compare_sb3_to_behavior_clone_anchor.py`, deterministic high-pressure comparisons, `validate_policy_window_regression.py`, failure-case review, and the RL acceptance manifest before it can become a test Bot candidate.

The first full distillation + PPO warm-start used 21,726 phase-aligned samples and the action-change staged GRU teacher. Five distillation epochs reached 0.6916 validation argmax accuracy, then 2,048 PPO timesteps on high-pressure maps completed. The policy still failed: all three 60-second maps triggered action-distribution repair, and all three 300-second maps recorded 0% win rate with action 3 dominant ratio above 0.76. Treat this as a repair result for the current teacher/reward setup, not a reason to promote PPO.

The first full target-entropy distillation used `--teacher-temperature 1.5 --uniform-target-mix 0.05`, raising target entropy to 1.186717. It improved the 60-second high-pressure comparison to 80% win rate on all three maps without triggering the compare script's action-bias repair, but the 300-second comparison still recorded 0% win rate on all three maps and shifted the long-run bias to action 6. Treat it as a short-window repair signal only.

Warm-start runs can override PPO entropy coefficient with `--model-in ... --ent-coef <value>` and learning rate with `--model-in ... --learning-rate <value>`. The training report records `algorithm_parameters_source` as `warm_start_metadata_with_overrides` when metadata is loaded and a CLI override is applied, so entropy/curriculum experiments remain auditable instead of silently inheriting the distilled zip defaults. Learning-rate overrides also refresh the loaded SB3 schedule before continuation training.

The first `ent_coef = 0.02` target-entropy warm-start lifted the 60-second high-pressure normalized entropy to 0.5801 / 0.5823 / 0.5307, but short-window win rates remained 80% / 60% / 80% and all three 300-second maps still recorded 0% win rate. Entropy override is a useful movement-diversity repair knob, not a replacement for long-run goals or upgrade supervision.

The first upgrade-choice export smoke produced 241 movement samples and 4 upgrade samples from 2 KiteBot seeds on `soda-creek`. Treat this as a supervised data-entry proof only; it does not prove upgrade policy quality, Gym action-mode support, or high-pressure long-run repair.

Use `train_upgrade_choice.py` for the first supervised upgrade-choice ranker smoke:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_upgrade_choice.py \
  --dataset harness/reports/2026-05-27_rl_upgrade_choice_export_smoke_001 \
  --epochs 20 \
  --batch-size 8 \
  --hidden-size 16 \
  --model-out harness/reports/local_upgrade_choice/upgrade_choice_smoke.pt \
  --report harness/reports/local_upgrade_choice/run_output.json
```

The ranker expands each upgrade prompt into one option row per offered upgrade, appends an upgrade-id one-hot feature to the observation, and learns which option the rule Bot chose. The first 4-choice smoke writes a checkpoint and `upgrade_choice_training_smoke_not_policy_gate`; it proves model plumbing only, not upgrade strategy quality.

Pass `--upgrade-choice-model` during training, `--evaluate-model`, or `--compare-rule-bots` to let the Gym bridge use that ranker for pending upgrade prompts:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --algorithm ppo \
  --evaluate-model \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --upgrade-choice-model harness/reports/2026-05-27_rl_upgrade_choice_training_smoke_001/upgrade_choice_smoke.pt \
  --eval-episodes 1 \
  --eval-seconds 60 \
  --seed-start 57000 \
  --map-id soda-creek \
  --report harness/reports/local_upgrade_choice_gym/evaluation.json
```

Evaluation reports record `upgrade_policy`, per-episode `upgrade_policy_decisions`, and summary `upgrade_policy_decision_count`. The first 60-second `soda-creek` smoke reached one upgrade prompt and recorded one ranker decision, but it remains `gym_upgrade_action_mode_smoke_not_policy_gate`; run normal 60/300-second high-pressure comparisons before treating any movement + upgrade-policy pair as useful.

Training reports also record `training.upgrade_choice_model`, top-level `upgrade_policy`, and the post-training evaluation `upgrade_policy_decision_count`. This proves the ranker was wired into closed-loop PPO/DQN training, but it still does not prove that the learned movement policy uses upgrades well.

For a slightly broader plumbing check, export upgrade samples from multiple maps and point the trainer at the report directory:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_upgrade_choice.py \
  --dataset harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001 \
  --epochs 20 \
  --batch-size 16 \
  --hidden-size 32 \
  --model-out harness/reports/local_upgrade_choice_multimap/upgrade_choice_multimap_smoke.pt \
  --report harness/reports/local_upgrade_choice_multimap/run_output.json
```

The first high-pressure multimap smoke used 64 upgrade prompts from `soda-creek`, `caramel-workshop`, and `cracked-star-jar`, then recorded Gym upgrade decisions on all three maps. It is still a smoke-only result, because the movement policy and ranker pair have not passed multi-seed 60/300-second acceptance.

The first movement+upgrade high-pressure comparison kept the upgrade ranker active but still failed: the legacy movement behavior clone selected action `3` for 100% of deterministic steps, and the 300-second high-pressure comparison reached 0% policy win rate on all three maps. Treat this as movement-policy repair evidence, not as a reason to continue scaling upgrade samples alone.

For movement behavior-clone experiments, train from exported movement trajectories:

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
