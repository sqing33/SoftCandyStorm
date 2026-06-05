# v61 人工审查表

- 候选 id：`2026-06-05_demo_buildcraft_repair_v61_full_pack`
- 内容 hash：`fnv1a64:66fa99c902f3af87`
- 人工试玩报告：`0` / `6`
- 人工试玩草稿仍有 TODO：`True`

## 规则

- [ ] 当前候选必须留在 generated_candidates，直到真人设计审查和人工试玩门禁通过。
- [ ] 填完这张表后，把具体观察写回 JSON 草稿，并运行对应校验。
- [ ] 不要用自动 demo-input、加速或 auto-exit 证据替代真人观察。
- [ ] Runtime GUI 当前环境如遇 GPU 不可用，只能记录阻塞，不能当作内容失败或人工试玩通过。

## 设计审查

- 草稿：`harness/content_review/drafts/2026-06-05_demo_buildcraft_repair_v61_full_pack_design_review_draft.json`
- 内容项：`route-memory-caramel-ring`
- 当前门禁结论：`draft_todo`

### route-memory-caramel-ring

- theme_fit: ____ / 5
- novelty: ____ / 5
- build_potential: ____ / 5
- counterplay_clarity: ____ / 5
- visual_audio_fit: ____ / 5
- balance_risk: low / medium / high
- decision: pass / revise / reject
- 重点观察：212-232 秒焦糖旧路环印是否能提示玩家换线，同时不让新手觉得突然不公平。
- 具体设计观察：

```text

```
- 必要修改或接受阻塞点：

```text

```

## 人工试玩局

- 草稿：`harness/playtest/drafts/2026-06-05_demo_buildcraft_repair_v61_manual_playtest_review_draft.json`
- 人工证据不得使用 `--demo-input`、`--simulation-speed` 或 `--auto-exit-after-report`。
- 6 局覆盖首发 5 个角色和 6 张地图；每局报告只是辅助，评分和结论必须由真人填写。

### new_frosting_jar_keeper

- 玩家视角：`new`
- 角色：`jar-keeper`
- 地图：`frosting-grassland`
- 固定 seed：`55301`
- 试玩意图：不看说明直接开局，确认新手是否理解移动、拾取糖晶和第一次升级
- 报告路径：`harness/telemetry/local/v61_manual_playtest_new_frosting_jar_keeper.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_current_manual_playtest.py new_frosting_jar_keeper`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id jar-keeper --map-id frosting-grassland --seed 55301 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v61_manual_playtest_new_frosting_jar_keeper.json --capture-interval 2`

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

### speed_soda_bubble_courier

- 玩家视角：`skilled`
- 角色：`bubble-courier`
- 地图：`soda-creek`
- 固定 seed：`55302`
- 试玩意图：主动利用速度穿插收 XP，确认泡泡邮差和汽水溪谷的移动压力
- 报告路径：`harness/telemetry/local/v61_manual_playtest_speed_soda_bubble_courier.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_current_manual_playtest.py speed_soda_bubble_courier`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id bubble-courier --map-id soda-creek --seed 55302 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v61_manual_playtest_speed_soda_bubble_courier.json --capture-interval 2`

#### 必看观察项

- [ ] 移动优势是否明显
- [ ] 泡泡敌人压力是否清楚
- [ ] 贪 XP 后是否知道受伤原因

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

### summon_cotton_pudding_crafter

- 玩家视角：`build`
- 角色：`pudding-crafter`
- 地图：`cotton-cloud-pasture`
- 固定 seed：`55303`
- 试玩意图：优先召唤和经济构筑，确认布丁工匠在群体压力下是否有成型目标
- 报告路径：`harness/telemetry/local/v61_manual_playtest_summon_cotton_pudding_crafter.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_current_manual_playtest.py summon_cotton_pudding_crafter`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id pudding-crafter --map-id cotton-cloud-pasture --seed 55303 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v61_manual_playtest_summon_cotton_pudding_crafter.json --capture-interval 2`

#### 必看观察项

- [ ] 召唤物反馈是否清楚
- [ ] 经济构筑是否有成长感
- [ ] 棉花云敌群是否可读

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

### control_caramel_sour_plum_doctor

- 玩家视角：`skilled`
- 角色：`sour-plum-doctor`
- 地图：`caramel-workshop`
- 固定 seed：`55304`
- 试玩意图：优先控场和减速路线，确认焦糖工坊路线干扰是否有趣而不烦
- 报告路径：`harness/telemetry/local/v61_manual_playtest_control_caramel_sour_plum_doctor.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_current_manual_playtest.py control_caramel_sour_plum_doctor`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id sour-plum-doctor --map-id caramel-workshop --seed 55304 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v61_manual_playtest_control_caramel_sour_plum_doctor.json --capture-interval 2`

#### 必看观察项

- [ ] 控场效果是否看得懂
- [ ] 路线干扰是否公平
- [ ] 后半段压力是否过度

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

### defense_jelly_cream_knight

- 玩家视角：`build`
- 角色：`cream-knight`
- 地图：`jelly-platform`
- 固定 seed：`55305`
- 试玩意图：优先防御和近身容错，确认奶油骑士在环形路线中的受伤反馈
- 报告路径：`harness/telemetry/local/v61_manual_playtest_defense_jelly_cream_knight.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_current_manual_playtest.py defense_jelly_cream_knight`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id cream-knight --map-id jelly-platform --seed 55305 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v61_manual_playtest_defense_jelly_cream_knight.json --capture-interval 2`

#### 必看观察项

- [ ] 防御成长是否能感受到
- [ ] 近身受伤反馈是否及时
- [ ] 果冻月台路线是否清晰

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

### final_cracked_jar_keeper

- 玩家视角：`skilled`
- 角色：`jar-keeper`
- 地图：`cracked-star-jar`
- 固定 seed：`55306`
- 试玩意图：挑战最终地图混合怪潮，确认首发包终局压力、Boss 出场和死亡原因
- 报告路径：`harness/telemetry/local/v61_manual_playtest_final_cracked_jar_keeper.json`
- 本地报告已存在：`False`
- 启动器：`python3 harness/playtest/run_current_manual_playtest.py final_cracked_jar_keeper`
- Runtime 命令：`cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-05_demo_buildcraft_repair_v61_full_pack --character-id jar-keeper --map-id cracked-star-jar --seed 55306 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v61_manual_playtest_final_cracked_jar_keeper.json --capture-interval 2`

#### 必看观察项

- [ ] Boss 出场是否明显
- [ ] 混合怪潮是否可读
- [ ] 死亡或胜利原因是否清楚

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
python3 harness/playtest/check_current_candidate_readiness.py --allow-incomplete
python3 harness/playtest/list_current_human_evidence_todos.py --allow-todos
python3 harness/content_review/check_current_design_review_status.py --allow-incomplete
python3 harness/playtest/check_current_manual_playtest_status.py --allow-incomplete
python3 harness/playtest/validate_manual_review.py harness/playtest/drafts/2026-06-05_demo_buildcraft_repair_v61_manual_playtest_review_draft.json --strict-acceptance
python3 harness/content_review/validate_content_candidate_design_review.py harness/content_review/drafts/2026-06-05_demo_buildcraft_repair_v61_full_pack_design_review_draft.json --repo-root .
```

这张表本身不是接受证据；JSON 草稿和 Runtime 报告才是后续校验的事实来源。
