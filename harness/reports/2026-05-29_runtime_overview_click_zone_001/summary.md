# Runtime Overview Click Zone

- Decision: `runtime_overview_click_zone_valid`
- Scope: `game_runtime` F1 overview right-bottom segmented pointer navigation zone

## Implemented

- F1 概览页新增鼠标左键四段点击区，点击区只在右侧局外面板范围和控制高度内生效。
- 四段从左到右映射为章节、图鉴、设置和巡逻准备页。
- 点击入口复用 `select_runtime_meta_panel`，继续写回 `base_ui_state.selected_panel`，并保留切换面板取消删除确认态的路径。
- 概览页点击切换后会结束当前帧，避免同一次点击被切换后的页面继续消费。
- F1 文本面板、Runtime surface contract 和基地 UI 人工审查模板已同步记录该入口。

## Verification

- `cargo test -p game_runtime`: 83 passed
- `cargo test --workspace`: 148 passed
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

- 这是文本面板分段点击区，不是发布级视觉基地 UI 或正式按钮布局。
- 当前证据来自源码形状与单测，不是真实鼠标设备人工审查。
- 该入口只切换已有局外面板，不解锁内容、不集成候选内容，也不让任何人工门禁通过。
- 不替代基地 UI 人工审查、真实设备审查、人工试玩、完整视觉基地 UI 或发布门禁。
