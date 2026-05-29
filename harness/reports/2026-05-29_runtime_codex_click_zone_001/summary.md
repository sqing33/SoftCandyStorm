# Runtime Codex Click Zone

- Decision: `runtime_codex_click_zone_valid`
- Scope: `game_runtime` F3 codex right-bottom segmented pointer control zone

## Implemented

- F3 图鉴页的鼠标左键入口现在必须落在右下分段点击区内，不再从窗口任意位置推进图鉴条目。
- 右下五段点击区从左到右映射为上一类、下一类、上一条、下一条和仅已发现过滤切换。
- 鼠标右键仍保留上一条快捷，鼠标中键仍保留过滤快捷。
- 点击区 helper 使用右侧局外面板宽度、右边距和底部控制高度，和现有右侧面板位置保持一致。
- F3 帮助文本同步展示右下点击区入口。

## Verification

- `cargo test -p game_runtime`: 71 passed
- `cargo test --workspace`: 136 passed
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

- 这是文本面板分段点击区，不是完整视觉按钮布局。
- 当前证据来自源码形状与单测，不是真实鼠标或触屏人工审查。
- 只读取当前 Runtime 内容包元数据和 `MetaProgress`，不加载 generated story/codex candidate 正文。
- 不替代剧情人工审校、Runtime UI review、final human acceptance、基地 UI 人工审查、Bevy smoke 或发布门禁。
