# RL Curriculum Plan

- Source: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_mix_001/late_contrast_pressure/failure_analysis_300s.json`
- Decision: `rl_curriculum_plan_created`
- Initial model: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip`
- Stage count: 2

## Stages

| Stage | Focus | Maps | Train Seconds | Eval Seconds | Timesteps |
|---:|---|---|---:|---:|---:|
| 1 | `opening_lt_60` | `cracked-star-jar`, `soda-creek` | 60 | 60 | 2048 |
| 2 | `late_180_to_300` | `caramel-workshop`, `cracked-star-jar`, `soda-creek` | 300 | 300 | 2048 |

## `stage_01_opening_lt_60`

- Reason: 2 map(s) recorded opening_lt_60 failures; train this stage separately so early deaths and late collapses do not hide each other.
- Model in: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip`
- Model out: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`

Train:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip --model-out harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --report-dir harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60 --train-maps cracked-star-jar,soda-creek --train-map-selection random --train-seconds 60 --timesteps 2048 --ent-coef 0.02 --reward-profile late-route-recovery --eval-episodes 3 --eval-seconds 60 --map-id cracked-star-jar --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/ppo_training_report.json
```

Compare:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 60 --seed-start 62700 --rule-bots random,kite,tank --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/comparison_60s.json
```

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 180 --seed-start 62700 --rule-bots random,kite,tank --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/comparison_180s.json
```

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 300 --seed-start 62700 --rule-bots random,kite,tank --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/comparison_300s.json
```


## `stage_02_late_180_to_300`

- Reason: 3 map(s) recorded late_180_to_300 failures; train this stage separately so early deaths and late collapses do not hide each other.
- Model in: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`
- Model out: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`

Train:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --model-out harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip --report-dir harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300 --train-maps caramel-workshop,cracked-star-jar,soda-creek --train-map-selection random --train-seconds 300 --timesteps 2048 --ent-coef 0.02 --reward-profile late-route-recovery --eval-episodes 3 --eval-seconds 300 --map-id caramel-workshop --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/ppo_training_report.json
```

Compare:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip --eval-episodes 3 --eval-seconds 60 --seed-start 62800 --rule-bots random,kite,tank --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/comparison_60s.json
```

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip --eval-episodes 3 --eval-seconds 180 --seed-start 62800 --rule-bots random,kite,tank --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/comparison_180s.json
```

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip --eval-episodes 3 --eval-seconds 300 --seed-start 62800 --rule-bots random,kite,tank --report harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/comparison_300s.json
```


## Limitations

- This manifest plans staged training commands only; it does not run PPO.
- Each stage must still be trained, compared against rule Bots, and recorded with failure cases if it fails.
- Stage ordering is based on failure time buckets and should be revised if new comparison evidence contradicts it.
