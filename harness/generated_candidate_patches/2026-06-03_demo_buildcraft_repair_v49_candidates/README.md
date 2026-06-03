# Demo Buildcraft Repair v49 Candidates

本批次基于 v48 继续修复首发可玩内容池，用于测试“控场路线补强 + Boss 专用强武器退出默认升级池”是否能降低 BossHunter / Route 过稳，同时保留糖霜草地 300 秒 Demo 的基础可玩性。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v48_full_pack`

目标：

- 只覆盖两个武器定义，不修改正式内容池。
- 小幅增强 `caramel-sticky-ground` 的区域覆盖和持续时间，帮助控场构筑处理 210 秒后怪潮。
- 将 `star-sugar-ray` 从默认升级池移到发现解锁，避免首发局内三选一过早出现 Boss 专用速杀路线。
- 不调整 `soda-bubble-pop`、`bubble-shoes`、彩虹糖弹或波次早期冲刺窗口；临时探针显示这些方向容易误伤 Coward / BossHunter 或没有解决 Kite 过稳。

改动：

- `caramel-sticky-ground.version`：`1 -> 2`
- `caramel-sticky-ground.base_stats.area_radius`：`44 -> 46`
- `caramel-sticky-ground.base_stats.duration_ms`：`3000 -> 3300`
- `caramel-sticky-ground.scaling.area_per_level`：`4 -> 5`
- `star-sugar-ray.version`：`5 -> 6`
- `star-sugar-ray.unlock.type`：`default -> discover`

探针结论：

- `/tmp/soft_candy_v49_probe_reports/star_out_5seed`：`boss-hunter` 与 `route` 回到目标区间；`greedy`、`kite`、`zone-control` 仍需 repair。
- `/tmp/soft_candy_v49_probe_reports/star_soda_out_5seed`：同时移出 `soda-bubble-pop` 会压低 `boss-hunter`，不采用。
- `/tmp/soft_candy_v49_probe_reports/caramel_pepper_5seed` 与 `caramel_spicy_5seed`：短窗口冲刺扰动会误伤低技能或 BossHunter，不采用。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. 72000-72009 all-Bot 300 秒矩阵
8. 若矩阵仍有 Bot 偏离目标区间，记录 failure case 后继续 v50 修复
