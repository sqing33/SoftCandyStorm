# 2026-05-25 mmx 第二批单体素材候选

本目录保存使用 `mmx` CLI 生成的第二批《软糖风暴》单体素材候选。目标是修复第一批 spritesheet 混杂、投影残留和身份不稳定的问题，改为分别生成玩家、敌人、pickup、projectile/effect 和 Boss。

## 候选内容

- `images/`：mmx 原始 JPG 输出。
- `processed/single_sprites_v002/`：使用 `tools/asset_postprocess.py key-singles` 后处理出的透明 PNG 候选。
- `review_previews/single_sprites_v002/`：128px、64px、32px 棋盘格预览和 192px 标准画布。
- `metadata/manifest.json`：生成 prompt、来源、QA 状态和下一步要求。
- `metadata/postprocess_single_sprites_v002.json`：单体抠图后处理报告。
- `metadata/preview_single_sprites_v002.json`：预览生成报告。
- `metadata/review_2026-05-25.md`：第二批素材候选审查结论。

## 准入状态

这些文件仍然只属于 `generated_candidates`，没有进入正式 `assets/`，也没有接入 Runtime。

第二批单体图比第一批更容易人工筛选，但仍没有稳定遵守纯色背景约束：部分输出为白底或浅色底，彩虹弹原图含水印痕迹。正式接入前必须重新生成或人工清理边缘、阴影、水印，并复核 32-64px 可读性。
