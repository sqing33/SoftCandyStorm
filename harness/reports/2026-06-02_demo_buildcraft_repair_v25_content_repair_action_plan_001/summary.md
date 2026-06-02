# v25 内容修复行动计划

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Decision: `v25_content_repair_action_plan_needs_playtest_reports`
- Action items: `21`
- Missing reports: `21`
- Report attention: `0`
- Objective metric risks: `0`

## 来源摘要

| Source | Decision | Existing | Missing | Attention |
|---|---|---:|---:|---:|
| `quick_play` | `quick_play_summary_no_reports` | 0 | 6 | 0 |
| `content_tour` | `content_tour_summary_no_reports` | 0 | 6 | 0 |
| `manual_playtest` | `manual_report_summary_no_reports` | 0 | 9 | 0 |

## 优先修复项

| Priority | Domain | Category | Item | Focus | Action | Command |
|---|---|---|---|---|---|---|
| `P0` | `quick_play` | `missing_report` | `quick_play_missing_default` | 糖罐守护员和糖霜草地基准体验 | 运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。 | `python3 harness/playtest/play_v25_candidate.py default` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_new_001` | 不看说明直接开始 | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py new_001` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_new_002` | 尝试贪 XP | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py new_002` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_new_003` | 保守绕圈 | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py new_003` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_skilled_001` | 主动拉怪收 XP | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py skilled_001` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_skilled_002` | 主动挑战 Boss | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py skilled_002` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_skilled_003` | 高压波次存活 | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py skilled_003` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_build_001` | 远程投射物优先 | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py build_001` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_build_002` | 防御 / 移速优先 | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py build_002` |
| `P0` | `manual_playtest` | `missing_report` | `manual_playtest_missing_build_003` | 控制 / 范围优先 | 运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。 | `python3 harness/playtest/run_v25_manual_playtest.py build_003` |
| `P1` | `quick_play` | `missing_report` | `quick_play_missing_speed` | 泡泡邮差和汽水溪谷移动压力 | 运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。 | `python3 harness/playtest/play_v25_candidate.py speed` |
| `P1` | `quick_play` | `missing_report` | `quick_play_missing_summon` | 布丁工匠和棉花云群体压力 | 运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。 | `python3 harness/playtest/play_v25_candidate.py summon` |
| `P1` | `quick_play` | `missing_report` | `quick_play_missing_control` | 酸梅博士和焦糖工坊路线干扰 | 运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。 | `python3 harness/playtest/play_v25_candidate.py control` |
| `P1` | `quick_play` | `missing_report` | `quick_play_missing_defense` | 奶油骑士和果冻月台环形路线 | 运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。 | `python3 harness/playtest/play_v25_candidate.py defense` |
| `P1` | `quick_play` | `missing_report` | `quick_play_missing_final` | 裂星糖罐混合怪潮压力 | 运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。 | `python3 harness/playtest/play_v25_candidate.py final` |
| `P1` | `content_tour` | `missing_report` | `content_tour_missing_frosting_jar_keeper` | 新手基准角色和糖霜草地开局 | 运行对应 content-tour 局，覆盖地图、角色和局内内容表面。 | `python3 harness/playtest/run_v25_content_tour.py frosting_jar_keeper` |
| `P1` | `content_tour` | `missing_report` | `content_tour_missing_soda_bubble_courier` | 速度角色和汽水溪谷泡泡压力 | 运行对应 content-tour 局，覆盖地图、角色和局内内容表面。 | `python3 harness/playtest/run_v25_content_tour.py soda_bubble_courier` |
| `P1` | `content_tour` | `missing_report` | `content_tour_missing_cotton_pudding_crafter` | 召唤角色和棉花云群体压力 | 运行对应 content-tour 局，覆盖地图、角色和局内内容表面。 | `python3 harness/playtest/run_v25_content_tour.py cotton_pudding_crafter` |
| `P1` | `content_tour` | `missing_report` | `content_tour_missing_caramel_sour_plum_doctor` | 控制角色和焦糖工坊路线干扰 | 运行对应 content-tour 局，覆盖地图、角色和局内内容表面。 | `python3 harness/playtest/run_v25_content_tour.py caramel_sour_plum_doctor` |
| `P1` | `content_tour` | `missing_report` | `content_tour_missing_jelly_cream_knight` | 防御角色和果冻月台环形路线 | 运行对应 content-tour 局，覆盖地图、角色和局内内容表面。 | `python3 harness/playtest/run_v25_content_tour.py jelly_cream_knight` |
| `P1` | `content_tour` | `missing_report` | `content_tour_missing_cracked_jar_keeper` | 最终地图混合怪潮压力 | 运行对应 content-tour 局，覆盖地图、角色和局内内容表面。 | `python3 harness/playtest/run_v25_content_tour.py cracked_jar_keeper` |

## 下一组命令

- `python3 harness/playtest/play_v25_candidate.py default`
- `python3 harness/playtest/run_v25_manual_playtest.py new_001`
- `python3 harness/playtest/run_v25_manual_playtest.py new_002`
- `python3 harness/playtest/run_v25_manual_playtest.py new_003`
- `python3 harness/playtest/run_v25_manual_playtest.py skilled_001`
- `python3 harness/playtest/summarize_v25_quick_play_reports.py --allow-incomplete`
- `python3 harness/playtest/summarize_v25_content_tour_reports.py --allow-incomplete`
- `python3 harness/playtest/summarize_v25_manual_playtest_reports.py --allow-incomplete`
- `python3 harness/playtest/create_v25_content_repair_action_plan.py`

## 限制

- 这份计划只整理 v25 候选内容的试玩修复线索，不批准、不接受、不晋级内容。
- 缺失报告、客观指标和自动 attention 只能告诉我们该看哪里，不能替代真人乐趣、清晰度和再来一局冲动判断。
- v25 仍必须通过设计审查、9 局人工试玩、最终接受和 lockfile 后，才能离开候选池。
- AI/RL 训练线不在本计划范围内。
