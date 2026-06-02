# v25 Human Review Worksheet

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Design TODOs: `14`
- Playtest TODOs: `101`
- Playtest runs: `9`

## Rules

- [ ] Keep v25 in generated_candidates until human design review and manual playtest gates pass.
- [ ] After filling this worksheet, copy concrete observations into the JSON drafts and run validators.
- [ ] Do not replace human observations with automated demo-input evidence.

## Design Review

- Draft: `harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json`
- Content item: `pudding-turret`
- Current gate decision: `needs_more_review`

### pudding-turret

- theme_fit: ____ / 5
- novelty: ____ / 5
- build_potential: ____ / 5
- counterplay_clarity: ____ / 5
- visual_audio_fit: ____ / 5
- balance_risk: low / medium / high
- decision: pass / revise / reject
- concrete design observation:

```text

```
- required changes or acceptance blocker:

```text

```

### Batch Notes

- reviewer: ____________________
- reviewed_at: YYYY-MM-DD
- summary:

```text

```
- batch risks:

```text

```
- next actions:

```text

```

## Manual Playtest Runs

- Draft: `harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`
- Human evidence must not use `--demo-input`, `--simulation-speed`, or `--auto-exit-after-report`.

### new_001

- skill: `new`
- seed: `25001`
- intent: 不看说明直接开始
- report: `harness/telemetry/local/v25_manual_playtest_new_001.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py new_001`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25001 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_001.json --capture-interval 2`

#### Required Observations

- [ ] 是否理解移动
- [ ] 是否理解拾取糖晶
- [ ] 是否理解升级三选一

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### new_002

- skill: `new`
- seed: `25002`
- intent: 尝试贪 XP
- report: `harness/telemetry/local/v25_manual_playtest_new_002.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py new_002`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25002 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_002.json --capture-interval 2`

#### Required Observations

- [ ] 是否知道为什么受伤
- [ ] 如果死亡是否知道主要原因
- [ ] XP 节奏是否诱导过度冒险

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### new_003

- skill: `new`
- seed: `25003`
- intent: 保守绕圈
- report: `harness/telemetry/local/v25_manual_playtest_new_003.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py new_003`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25003 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_003.json --capture-interval 2`

#### Required Observations

- [ ] 前 2 分钟是否至少看到 2-3 次升级机会
- [ ] 保守玩法是否太无聊
- [ ] 怪潮压力是否逐步增加

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### skilled_001

- skill: `skilled`
- seed: `25011`
- intent: 主动拉怪收 XP
- report: `harness/telemetry/local/v25_manual_playtest_skilled_001.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py skilled_001`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25011 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_001.json --capture-interval 2`

#### Required Observations

- [ ] 命中反馈是否清楚
- [ ] XP 拾取是否顺畅
- [ ] 升级选择是否有纠结

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### skilled_002

- skill: `skilled`
- seed: `25012`
- intent: 主动挑战 Boss
- report: `harness/telemetry/local/v25_manual_playtest_skilled_002.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py skilled_002`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25012 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_002.json --capture-interval 2`

#### Required Observations

- [ ] Boss 出场是否明显
- [ ] Boss 威胁方向是否明确
- [ ] Boss 战是否拖沓

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### skilled_003

- skill: `skilled`
- seed: `25013`
- intent: 高压波次存活
- report: `harness/telemetry/local/v25_manual_playtest_skilled_003.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py skilled_003`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25013 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_003.json --capture-interval 2`

#### Required Observations

- [ ] 屏幕压力是否压迫但不烦
- [ ] 受伤反馈是否及时
- [ ] 性能体感是否稳定

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### build_001

- skill: `build`
- seed: `25021`
- intent: 远程投射物优先
- report: `harness/telemetry/local/v25_manual_playtest_build_001.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py build_001`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25021 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_001.json --capture-interval 2`

#### Required Observations

- [ ] projectile 可读性
- [ ] 单体输出反馈
- [ ] 远程 Build 是否有明确优势和代价

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### build_002

- skill: `build`
- seed: `25022`
- intent: 防御 / 移速优先
- report: `harness/telemetry/local/v25_manual_playtest_build_002.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py build_002`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25022 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_002.json --capture-interval 2`

#### Required Observations

- [ ] 受伤反馈
- [ ] 逃生空间
- [ ] 容错感

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

### build_003

- skill: `build`
- seed: `25023`
- intent: 控制 / 范围优先
- report: `harness/telemetry/local/v25_manual_playtest_build_003.json`
- report exists: `False`
- launcher: `python3 harness/playtest/run_v25_manual_playtest.py build_003`
- runtime command: `cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25023 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_003.json --capture-interval 2`

#### Required Observations

- [ ] 地面效果可读性
- [ ] 敌群可读性
- [ ] 性能体感

#### Ratings

- fun_rating: ____ / 5
- clarity_rating: ____ / 5
- difficulty_rating: ____ / 5
- projectile_readability: ____ / 5
- hit_feedback: ____ / 5
- xp_pickup_rhythm: ____ / 5
- boss_spawn_clarity: ____ / 5
- death_reason_clarity: ____ / 5
- gate_decision: playtest_pass / repair / needs_more_runs
- tags: __________________________________
- concrete moment-to-moment observation:

```text

```
- next actions:

```text

```

## Validation Commands

```bash
python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete
python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete
python3 harness/playtest/check_v25_candidate_readiness.py --allow-incomplete
python3 harness/playtest/list_v25_human_evidence_todos.py --allow-todos
```

This worksheet is not acceptance evidence by itself; the JSON drafts remain the source of truth.
