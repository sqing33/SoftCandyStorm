# RL Fixed-window Action Plan

- Decision: `rl_fixed_window_action_plan_ready`
- Initial model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Reward profile: `late-route-recovery`
- Stages: 3
- Validation windows: 60, 180, 300

## Sources

| Label | Seconds | Decision | Failure Groups | Total Failures |
|---|---:|---|---:|---:|
| `60s` | 60.0 | `rl_policy_failure_analysis_recorded` | 1 | 1 |
| `180s` | 180.0 | `rl_policy_failure_analysis_recorded` | 3 | 3 |
| `300s` | 300.0 | `rl_policy_failure_analysis_recorded` | 5 | 9 |

## Stages

### stage_01_opening_lt_60

- Focus: `opening_lt_60`
- Title: opening retention repair
- Strategy: Protect short-window movement before any mid or late continuation.
- Train maps: `soda-creek`
- Source windows: 60, 180, 300
- Total failures: 4
- Train command: `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip --model-out harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --report-dir harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60 --train-maps soda-creek --train-map-selection random --train-seconds 60 --timesteps 256 --reward-profile late-route-recovery --eval-episodes 3 --eval-seconds 60 --map-id soda-creek --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/ppo_training_report.json`

Validation commands:
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 60 --seed-start 63400 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/comparison_60s.json`
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 180 --seed-start 63400 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/comparison_180s.json`
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 300 --seed-start 63400 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/comparison_300s.json`

### stage_02_mid_60_to_180

- Focus: `mid_60_to_180`
- Title: handoff and mid-window retention repair
- Strategy: Repair post-opening handoff without regressing the 60 second gate.
- Train maps: `cracked-star-jar`, `soda-creek`
- Source windows: 180, 300
- Total failures: 3
- Train command: `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --model-out harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --report-dir harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180 --train-maps cracked-star-jar,soda-creek --train-map-selection random --train-seconds 180 --timesteps 256 --reward-profile late-route-recovery --eval-episodes 3 --eval-seconds 180 --map-id cracked-star-jar --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/ppo_training_report.json`

Validation commands:
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --eval-episodes 3 --eval-seconds 60 --seed-start 63500 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/comparison_60s.json`
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --eval-episodes 3 --eval-seconds 180 --seed-start 63500 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/comparison_180s.json`
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --eval-episodes 3 --eval-seconds 300 --seed-start 63500 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/comparison_300s.json`

### stage_03_late_180_to_300

- Focus: `late_180_to_300`
- Title: late conversion repair
- Strategy: Improve late route recovery and 300 second conversion while preserving earlier windows.
- Train maps: `caramel-workshop`, `cracked-star-jar`, `soda-creek`
- Source windows: 300
- Total failures: 6
- Train command: `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --model-out harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip --report-dir harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300 --train-maps caramel-workshop,cracked-star-jar,soda-creek --train-map-selection random --train-seconds 300 --timesteps 256 --reward-profile late-route-recovery --eval-episodes 3 --eval-seconds 300 --map-id caramel-workshop --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/ppo_training_report.json`

Validation commands:
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip --eval-episodes 3 --eval-seconds 60 --seed-start 63600 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/comparison_60s.json`
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip --eval-episodes 3 --eval-seconds 180 --seed-start 63600 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/comparison_180s.json`
- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip --eval-episodes 3 --eval-seconds 300 --seed-start 63600 --rule-bots random,kite,tank --report harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_03_late_180_to_300/comparison_300s.json`

## Limitations

- This plan is generated from existing fixed-window diagnostic reports only.
- It does not train, evaluate, or approve a policy.
- Every suggested follow-up must still pass fixed-window no-regression and RL acceptance gates.
