# Runtime Codex Pointer Input

- Decision: `runtime_codex_pointer_input_valid`
- Scope: `game_runtime` F3 codex pointer entry and filter input

## Implemented

- F3 图鉴页现在在键盘之外接受鼠标指针按钮输入。
- 鼠标左键映射到下一条图鉴条目，等价于 `N`。
- 鼠标右键映射到上一条图鉴条目，等价于 `B`。
- 鼠标中键映射到仅已发现 / 全部条目过滤切换，等价于 `V`。
- F3 帮助文本同步展示键盘和鼠标入口。
- Runtime surface contract 已记录 `MouseButton::Left`、`MouseButton::Right` 和 `MouseButton::Middle` 的源码形状。

## Verification

- `cargo test -p game_runtime`: 69 passed
- `cargo test --workspace`: 134 passed
- `cargo clippy --workspace --all-targets`: passed
- `cargo fmt --check`: passed
- `python3 harness/runtime_contract/validate_runtime_surface_contract.py ...`: `runtime_surface_contract_valid`
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- `python3 tools/validate_base_ui_manual_review.py ...`: `base_ui_manual_review_invalid`，符合模板仍需真人填写的预期
- `python3 tools/validate_docs_implementation_coverage.py ... --allow-incomplete`: `docs_implementation_incomplete`，符合长目标未完成的预期
- `python3 tools/validate_progress_reports.py ...`: `progress_reports_valid`
- `python3 tools/validate_goal_evidence_consistency.py ...`: `goal_evidence_consistent`

## Limitations

- 这是文本面板指针输入原型，不是完整视觉可点击图鉴布局。
- 尚未加入手柄导航。
- 只读取当前 Runtime 内容包元数据和 `MetaProgress`，不加载 generated story/codex candidate 正文。
- 不替代剧情人工审校、Runtime UI review、final human acceptance、基地 UI 人工审查、Bevy smoke 或发布门禁。
