# 2026-05-25 素材候选清理批次

本批次不是新正式素材，而是对前两批 `mmx` repair 候选做二次清理与小尺寸复核。

## 范围

- 来源批次：`2026-05-25_mmx_second_pass`
- 来源批次：`2026-05-25_mmx_projectile_retry`
- 处理对象：玩家、普通软糖怪、XP 糖晶、暴走搅糖机 Boss、彩虹糖弹 `v003_002`
- 排除对象：`effect_rainbow_candy_shot_v002` 已因水印和火箭化身份判定为 `reject_regenerate`

## 输出

- `processed/cleaned_runtime_candidates/`：保留主体 alpha 连通组件后的透明 PNG 候选。
- `review_previews/cleaned_runtime_candidates/runtime_32/`：32px 透明候选预览。
- `review_previews/cleaned_runtime_candidates/preview_32/`：32px 棋盘格检查预览。
- `review_previews/cleaned_runtime_candidates/contact_sheet_32.png`：32px 汇总检查图。
- `metadata/component_cleanup_v001.json`：连通组件清理报告。
- `metadata/preview_cleaned_runtime_v001.json`：预览和 runtime-size 输出报告。
- `metadata/review_2026-05-25.md`：审查结论。

## 结论

本批次将彩虹糖弹左侧星光、糖晶和 Boss 的离散投影/阴影组件移除，并输出 128px、64px、32px 透明候选与棋盘格预览。

全部结果仍停留在 `generated_candidates`，不得直接进入正式 `assets/` 或 Runtime。玩家和 Boss 仍存在非严格俯视角风险，需要人工确认或用 `mmx` 重新生成更严格的 top-down 版本。
