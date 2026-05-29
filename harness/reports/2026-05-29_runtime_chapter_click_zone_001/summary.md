# Runtime Chapter Click Zone

- Decision: `runtime_chapter_click_zone_valid`
- Scope: `game_runtime` F2 chapter-goals right-bottom segmented pointer control zone

## Implemented

- F2 章节目标页新增鼠标左键三段点击区，点击区只在右侧局外面板范围和控制高度内生效。
- 三段从左到右映射为上一章、下一章和巡逻当前章节。
- 点击入口复用 `RuntimeChapterAction`，并继续落到现有 `apply_runtime_chapter_action` 路径。
- 锁定章节仍会拒绝启动；已解锁章节启动仍会切换地图、重开当前巡逻并保留局外进度。
- F2 文本面板、Runtime surface contract 和基地 UI 人工审查模板已同步记录该入口。

## Verification

- `cargo test -p game_runtime`: 81 passed
- `cargo test --workspace`: 146 passed
- `cargo clippy --workspace --all-targets`: passed
- `cargo fmt --check`: passed
- `python3 harness/runtime_contract/validate_runtime_surface_contract.py ...`: `runtime_surface_contract_valid`
- `python3 tools/validate_base_ui_manual_review.py ...`: `base_ui_manual_review_invalid`，符合模板仍需真人填写的预期
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- `python3 tools/test_validate_base_ui_manual_review.py`: 7 passed
- `python3 tools/validate_docs_implementation_coverage.py ... --allow-incomplete`: `docs_implementation_incomplete`，符合长目标未完成的预期
- `python3 tools/test_validate_docs_implementation_coverage.py`: 5 passed
- `python3 tools/validate_progress_reports.py ...`: `progress_reports_valid`
- `python3 tools/test_validate_progress_reports.py`: 6 passed
- `python3 tools/validate_goal_evidence_consistency.py ...`: `goal_evidence_consistent`
- `python3 tools/test_validate_goal_evidence_consistency.py`: 5 passed

## Limitations

- 这是文本面板分段点击区，不是发布级视觉按钮布局。
- 当前证据来自源码形状与单测，不是真实鼠标设备人工审查。
- 该入口只操作 `MetaProgress` 章节名册，不解锁章节，也不绕过锁定章节阻挡。
- 不替代基地 UI 人工审查、真实设备审查、人工试玩、完整视觉基地 UI 或发布门禁。
