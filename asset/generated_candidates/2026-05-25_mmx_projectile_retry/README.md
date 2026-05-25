# 2026-05-25 mmx 彩虹糖弹重生成候选

本目录保存使用 `mmx` CLI 重新生成的《软糖风暴》彩虹糖弹素材候选。目标是修复第二批单体素材中 `effect_rainbow_candy_shot_v002` 的水印痕迹、火箭化轮廓和背景不合规问题。

## 候选内容

- `images/`：mmx 原始 JPG 输出。
- `processed/projectile_v003/`：使用 `tools/asset_postprocess.py key-singles` 后处理出的透明 PNG 候选。
- `review_previews/projectile_v003/`：128px 标准透明画布，以及 64px、32px 棋盘格预览。
- `metadata/manifest.json`：生成 prompt、来源、QA 状态和下一步要求。
- `metadata/postprocess_projectile_v003.json`：单体抠图后处理报告。
- `metadata/preview_projectile_v003.json`：预览生成报告。
- `metadata/review_2026-05-25.md`：彩虹糖弹重生成审查结论。

## 准入状态

这些文件仍然只属于 `generated_candidates`，没有进入正式 `assets/`，也没有接入 Runtime。

本批次比 `effect_rainbow_candy_shot_v002` 更接近可用素材：背景更接近绿幕，未观察到明显文字或水印，`projectile_rainbow_candy_bullet_v003_002` 在 64px 和 32px 下有清晰圆形彩虹糖弹身份。正式接入前仍需要人工清理边缘、阴影和星光残留，并决定是否使用静态糖球版本或保留带尾迹的飞行版本。
