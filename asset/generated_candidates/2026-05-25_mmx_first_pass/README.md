# 2026-05-25 mmx 第一批素材候选

本目录保存使用 `mmx` CLI 生成的第一批《软糖风暴》素材候选，仅用于候选审查和后处理验证。

## 候选内容

- `images/runtime_spritesheet_v001_001.jpg`：Runtime 原型 spritesheet 候选。
- `processed/runtime_spritesheet_v001/`：从 Runtime 原型 spritesheet 切出的 25 个 PNG 候选。
- `audio/voice_storm_alert_v001.mp3`：中文风暴提示语音候选。
- `music/bgm_candy_battle_loop_v001.mp3`：糖果风战斗 BGM 候选。
- `metadata/postprocess_runtime_spritesheet_v001.json`：spritesheet 后处理报告。
- `metadata/review_2026-05-25.md`：第一批素材候选审查结论。

## 准入状态

这些文件没有进入正式 `assets/` 目录，也没有接入 Runtime。后续必须经过人工选择、后处理、格式整理和必要的授权/来源记录复核后，才允许进入正式素材目录。

当前图像候选没有遵守绿幕背景约束，实际为白底并带投影，需要抠图、裁切、转 PNG 和小尺寸可读性复核。

已使用 `tools/asset_postprocess.py` 做第一轮连通背景移除和网格裁切。输出 PNG 仍有原始投影残留，不能直接晋级为正式素材；后续需要人工挑选可用格子，必要时重新生成更严格的绿幕版本。

已完成第一轮候选审查，结论为 `repair`：少量 PNG 可进入二次清理，语音和 BGM 仅保留为人工听感审查候选，全部仍不得接入正式 Runtime。
