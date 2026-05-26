# 2026-05-26 mmx Runtime 俯视角与音频候选

本目录保存按 `harness/asset_review/mmx_asset_generation_plan_template.json` 执行的 `mmx` 素材候选批次。内容只用于候选审查、后处理验证和后续人工评估，不进入正式 `assets/`，不接入 Runtime。

## 候选内容

- `images/player_jar_keeper_topdown_v005_001.jpg` 和 `images/player_jar_keeper_topdown_v005_002.jpg`：玩家糖罐守护者俯视角 sprite 原图候选。
- `processed/topdown_v005_clean/`：从原图抠出并清理后的 PNG 候选。
- `review_previews/topdown_v005/`：128/64/32 像素透明 runtime-size 候选、棋盘格预览和 contact sheet。
- `audio/voice_boss_arrival_cn_v002.mp3`：Boss 出场中文语音候选。
- `music/sting_boss_arrival_v002_source.mp3`：Boss 出场音乐源候选。
- `processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3`：从音乐源候选裁剪出的 8 秒 sting 候选。
- `metadata/manifest.json`：候选文件、prompt、命令、来源、状态和下一步。
- `metadata/postprocess_topdown_v005.json`、`metadata/component_cleanup_topdown_v005.json`、`metadata/preview_topdown_v005.json`：图像后处理记录。
- `metadata/postprocess_audio_v002.json`：音频裁剪记录。
- `metadata/review_2026-05-26.md`：初步审查结论。

## 状态

本批次仍为 `generated_candidates`。图像候选需要人工检查是否真正满足俯视角、是否存在伪文字或透明边缘问题；语音和音乐需要人工听感、响度、可关闭设置和与战斗音效叠放检查。当前没有任何素材被标记为 `accepted_content`、`runtime_integrated` 或 `release_ready`。
