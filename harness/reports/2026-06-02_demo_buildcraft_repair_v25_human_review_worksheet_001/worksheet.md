# v25 人工审查表

- 候选 id：`2026-06-02_demo_buildcraft_repair_v25_full_pack`
- 内容 hash：`fnv1a64:aab110776109609d`
- 设计审查 TODO 数：`14`
- 人工试玩 TODO 数：`101`
- 人工试玩局数：`9`

## 规则

- [ ] v25 必须留在 generated_candidates，直到真人设计审查和人工试玩门禁通过。
- [ ] 填完这张表后，把具体观察写回 JSON 草稿，并运行对应校验。
- [ ] 不要用自动 demo-input 证据替代真人观察。

## 设计审查

- 草稿：`harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json`
- 内容项：`pudding-turret`
- 当前门禁结论：`needs_more_review`

### pudding-turret

- theme_fit: ____ / 5
- novelty: ____ / 5
- build_potential: ____ / 5
- counterplay_clarity: ____ / 5
- visual_audio_fit: ____ / 5
- balance_risk: low / medium / high
- decision: pass / revise / reject
- 具体设计观察：

```text

```
- 必要修改或接受阻塞点：

```text

```

### 批次备注

- reviewer: ____________________
- reviewed_at: YYYY-MM-DD
- 总结：

```text

```
- 批次风险：

```text

```
- 后续行动：

```text

```

## 人工试玩局

- 草稿：`harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`
- 人工证据不得使用 `--demo-input`、`--simulation-speed` 或 `--auto-exit-after-report`。

### new_001

- 玩家视角：`new`
- 固定 seed：`25001`
- 试玩意图：不看说明直接开始
- 报告路径：`harness/telemetry/local/v25_manual_playtest_new_001.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py new_001`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25001 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_001.json --capture-interval 2`

#### 必看观察项

- [ ] 是否理解移动
- [ ] 是否理解拾取糖晶
- [ ] 是否理解升级三选一

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### new_002

- 玩家视角：`new`
- 固定 seed：`25002`
- 试玩意图：尝试贪 XP
- 报告路径：`harness/telemetry/local/v25_manual_playtest_new_002.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py new_002`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25002 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_002.json --capture-interval 2`

#### 必看观察项

- [ ] 是否知道为什么受伤
- [ ] 如果死亡是否知道主要原因
- [ ] XP 节奏是否诱导过度冒险

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### new_003

- 玩家视角：`new`
- 固定 seed：`25003`
- 试玩意图：保守绕圈
- 报告路径：`harness/telemetry/local/v25_manual_playtest_new_003.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py new_003`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25003 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_003.json --capture-interval 2`

#### 必看观察项

- [ ] 前 2 分钟是否至少看到 2-3 次升级机会
- [ ] 保守玩法是否太无聊
- [ ] 怪潮压力是否逐步增加

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### skilled_001

- 玩家视角：`skilled`
- 固定 seed：`25011`
- 试玩意图：主动拉怪收 XP
- 报告路径：`harness/telemetry/local/v25_manual_playtest_skilled_001.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py skilled_001`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25011 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_001.json --capture-interval 2`

#### 必看观察项

- [ ] 命中反馈是否清楚
- [ ] XP 拾取是否顺畅
- [ ] 升级选择是否有纠结

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### skilled_002

- 玩家视角：`skilled`
- 固定 seed：`25012`
- 试玩意图：主动挑战 Boss
- 报告路径：`harness/telemetry/local/v25_manual_playtest_skilled_002.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py skilled_002`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25012 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_002.json --capture-interval 2`

#### 必看观察项

- [ ] Boss 出场是否明显
- [ ] Boss 威胁方向是否明确
- [ ] Boss 战是否拖沓

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### skilled_003

- 玩家视角：`skilled`
- 固定 seed：`25013`
- 试玩意图：高压波次存活
- 报告路径：`harness/telemetry/local/v25_manual_playtest_skilled_003.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py skilled_003`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25013 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_003.json --capture-interval 2`

#### 必看观察项

- [ ] 屏幕压力是否压迫但不烦
- [ ] 受伤反馈是否及时
- [ ] 性能体感是否稳定

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### build_001

- 玩家视角：`build`
- 固定 seed：`25021`
- 试玩意图：远程投射物优先
- 报告路径：`harness/telemetry/local/v25_manual_playtest_build_001.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py build_001`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25021 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_001.json --capture-interval 2`

#### 必看观察项

- [ ] projectile 可读性
- [ ] 单体输出反馈
- [ ] 远程 Build 是否有明确优势和代价

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### build_002

- 玩家视角：`build`
- 固定 seed：`25022`
- 试玩意图：防御 / 移速优先
- 报告路径：`harness/telemetry/local/v25_manual_playtest_build_002.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py build_002`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25022 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_002.json --capture-interval 2`

#### 必看观察项

- [ ] 受伤反馈
- [ ] 逃生空间
- [ ] 容错感

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

### build_003

- 玩家视角：`build`
- 固定 seed：`25023`
- 试玩意图：控制 / 范围优先
- 报告路径：`harness/telemetry/local/v25_manual_playtest_build_003.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_v25_manual_playtest.py build_003`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25023 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_003.json --capture-interval 2`

#### 必看观察项

- [ ] 地面效果可读性
- [ ] 敌群可读性
- [ ] 性能体感

#### 评分

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
- 具体局内观察：

```text

```
- 后续行动：

```text

```

## 校验命令

```bash
python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete
python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete
python3 harness/playtest/check_v25_candidate_readiness.py --allow-incomplete
python3 harness/playtest/list_v25_human_evidence_todos.py --allow-todos
```

这张表本身不是接受证据；JSON 草稿仍是事实来源。
