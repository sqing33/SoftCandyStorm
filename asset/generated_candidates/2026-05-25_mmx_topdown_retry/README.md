# 2026-05-25 mmx 严格俯视角重试候选

本批次使用 `mmx image generate` 重试玩家和暴走搅糖机 Boss 的严格俯视角素材。

## 目标

- 修复第二批单体素材中玩家和 Boss 偏正面插画的问题。
- 继续保持可爱糖果肉鸽风格。
- 输出透明 PNG、128px/64px/32px runtime-size 候选和棋盘格预览。

## 输出

- `images/`：`mmx` 原始 JPG。
- `processed/topdown_v004/`：首次抠图 PNG。
- `processed/topdown_v004_clean/`：alpha 连通组件清理后的 PNG。
- `review_previews/topdown_v004/runtime_32/`：32px 透明候选预览。
- `review_previews/topdown_v004/contact_sheet_32.png`：32px 棋盘格汇总图。
- `metadata/review_2026-05-25.md`：审查结论。

## 结论

本批次仍未稳定达到严格俯视角。玩家 `v004_002` 和 Boss `v004_002` 比较适合作为风格参考，但仍偏正面吉祥物，不得直接进入正式 `assets/` 或 Runtime。

后续如果坚持俯视角统一，建议继续重写 prompt，强调“only top surfaces visible, no front face, no standing body”，或改用手工/程序化占位素材先满足 Runtime 规格。
