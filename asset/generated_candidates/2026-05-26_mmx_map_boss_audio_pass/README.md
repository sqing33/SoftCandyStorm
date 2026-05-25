# 2026-05-26 mmx 地图与 Boss 音频候选

本目录保存使用 `mmx` CLI 生成的《软糖风暴》地图选择背景与 Boss 出场音频素材候选，仅用于候选审查、听感检查和后续后处理验证。

## 候选内容

- `images/map_select_background_v001_001.jpg`：地图选择界面背景图候选。
- `audio/voice_boss_arrival_v001.mp3`：裂星糖罐核心 Boss 出场中文语音提示候选。
- `music/sting_boss_arrival_v001.mp3`：Boss 出场音乐动机候选。
- `processed/audio_v001/sting_boss_arrival_v001_trim8s.mp3`：从 Boss 出场音乐候选剪辑出的 8 秒 sting 候选。
- `review_previews/map_select_background_v001/`：地图背景 640px 预览和地图卡牌覆盖预览。
- `metadata/manifest.json`：生成命令、prompt、格式、大小和门禁说明。
- `metadata/postprocess_audio_v001.json`：Boss 出场音乐剪辑后处理记录。
- `metadata/review_2026-05-26.md`：初步审查结论。

## 准入状态

全部文件仍停留在 `asset/generated_candidates/`，不得直接进入正式 `assets/` 或 Runtime。

地图背景需要人工检查是否存在伪文字、地标可读性和 UI 留白；语音需要人工听感审查、响度统一和可关闭设置；Boss 音乐原始生成时长约 102 秒，已剪出 8 秒 sting 候选，但仍需人工听感审查和与语音叠放检查。
