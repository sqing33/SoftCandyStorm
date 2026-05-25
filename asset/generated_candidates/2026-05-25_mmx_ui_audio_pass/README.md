# 2026-05-25 mmx UI 与音频候选

本目录保存使用 `mmx` CLI 生成的《软糖风暴》UI 与音频素材候选，仅用于候选审查、听感检查和后续后处理验证。

## 候选内容

- `images/ui_upgrade_card_frame_v001_001.jpg`：升级卡牌框 UI 候选。
- `processed/ui_v001/`：对升级卡牌框候选做背景移除后的 PNG。
- `review_previews/ui_v001/`：128px 标准画布与 64/32px 棋盘格预览。
- `audio/voice_level_up_prompt_v001.mp3`：中文升级提示语音候选。
- `music/jingle_run_settlement_v001.mp3`：局后结算 / 胜利 jingle 候选。
- `metadata/manifest.json`：生成命令、prompt、格式和门禁说明。
- `metadata/review_2026-05-25.md`：初步审查结论。

## 准入状态

全部文件仍停留在 `asset/generated_candidates/`，不得直接进入正式 `assets/` 或 Runtime。

UI 图像原始输出没有遵守绿幕背景，已做一轮自动背景移除和小尺寸预览，但仍需要人工检查阴影残留、边框可读性和升级界面适配；音频需要人工听感审查、响度统一、循环点/结尾复核和授权/来源记录确认。
