# RL Curriculum Plan

- Source: `harness/reports/2026-05-27_rl_failure_analysis_time_phase_balance_ppo_300s_001/failure_analysis.json`
- Decision: `rl_curriculum_plan_created`
- Initial model: `harness/reports/2026-05-27_rl_ppo_time_phase_balance_closed_loop_10k_001/ppo_time_phase_balance_closed_loop_10k.zip`
- Stage count: 3

## Stages

| Stage | Focus | Maps | Train Seconds | Eval Seconds | Timesteps |
|---:|---|---|---:|---:|---:|
| 1 | `opening_lt_60` | `cracked-star-jar`, `soda-creek` | 60 | 60 | 5000 |
| 2 | `mid_60_to_180` | `caramel-workshop` | 180 | 180 | 5000 |
| 3 | `late_180_to_300` | `caramel-workshop`, `cracked-star-jar`, `soda-creek` | 300 | 300 | 5000 |

## `stage_01_opening_lt_60`

- Reason: 2 map(s) recorded opening_lt_60 failures; train this stage separately so early deaths and late collapses do not hide each other.
- Model in: `harness/reports/2026-05-27_rl_ppo_time_phase_balance_closed_loop_10k_001/ppo_time_phase_balance_closed_loop_10k.zip`
- Model out: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`

Train:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-27_rl_ppo_time_phase_balance_closed_loop_10k_001/ppo_time_phase_balance_closed_loop_10k.zip --model-out harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --report-dir harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60 --train-maps cracked-star-jar,soda-creek --train-map-selection random --train-seconds 60 --timesteps 5000 --ent-coef 0.02 --eval-episodes 3 --eval-seconds 60 --map-id cracked-star-jar --report harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/ppo_training_report.json
```

Compare:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --eval-episodes 3 --eval-seconds 60 --seed-start 62100 --rule-bots random,kite,tank --report harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/comparison_60s.json
```

## `stage_02_mid_60_to_180`

- Reason: 1 map(s) recorded mid_60_to_180 failures; train this stage separately so early deaths and late collapses do not hide each other.
- Model in: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`
- Model out: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip`

Train:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip --model-out harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --report-dir harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180 --train-maps caramel-workshop --train-map-selection random --train-seconds 180 --timesteps 5000 --ent-coef 0.02 --eval-episodes 3 --eval-seconds 180 --map-id caramel-workshop --report harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/ppo_training_report.json
```

Compare:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --eval-episodes 3 --eval-seconds 180 --seed-start 62200 --rule-bots random,kite,tank --report harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/comparison_180s.json
```

## `stage_03_late_180_to_300`

- Reason: 3 map(s) recorded late_180_to_300 failures; train this stage separately so early deaths and late collapses do not hide each other.
- Model in: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip`
- Model out: `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip`

Train:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --model-in harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_02_mid_60_to_180/stage_02_mid_60_to_180.zip --model-out harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip --report-dir harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_03_late_180_to_300 --train-maps caramel-workshop,cracked-star-jar,soda-creek --train-map-selection random --train-seconds 300 --timesteps 5000 --ent-coef 0.02 --eval-episodes 3 --eval-seconds 300 --map-id caramel-workshop --report harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_03_late_180_to_300/ppo_training_report.json
```

Compare:

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_03_late_180_to_300/stage_03_late_180_to_300.zip --eval-episodes 3 --eval-seconds 300 --seed-start 62300 --rule-bots random,kite,tank --report harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/stages/stage_03_late_180_to_300/comparison_300s.json
```

## Limitations

- This manifest plans staged training commands only; it does not run PPO.
- Each stage must still be trained, compared against rule Bots, and recorded with failure cases if it fails.
- Stage ordering is based on failure time buckets and should be revised if new comparison evidence contradicts it.
