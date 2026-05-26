# Asset Audio Technical Probe

- Root: `asset/generated_candidates`
- Decision: `asset_audio_technical_probe_valid`
- Batches: 9
- Audio assets: 14
- ffprobe: `/opt/homebrew/bin/ffprobe`

## Batches

| Batch | Audio assets | Errors | Warnings |
|---|---:|---:|---:|
| `2026-05-25_asset_cleanup_pass` | 0 | 0 | 0 |
| `2026-05-25_mmx_first_pass` | 2 | 0 | 0 |
| `2026-05-25_mmx_projectile_retry` | 0 | 0 | 0 |
| `2026-05-25_mmx_second_pass` | 0 | 0 | 0 |
| `2026-05-25_mmx_topdown_retry` | 0 | 0 | 0 |
| `2026-05-25_mmx_ui_audio_pass` | 2 | 0 | 0 |
| `2026-05-26_mmx_level_up_feedback_pack` | 3 | 0 | 0 |
| `2026-05-26_mmx_map_boss_audio_pass` | 3 | 0 | 0 |
| `2026-05-26_mmx_runtime_topdown_audio_plan` | 4 | 0 | 0 |

## Audio Assets

| Batch | Asset | Type | Path | Duration | Sample rate | Channels |
|---|---|---|---|---:|---:|---:|
| `2026-05-25_mmx_first_pass` | `voice_storm_alert_v001` | `speech` | `audio/voice_storm_alert_v001.mp3` | 3.19275 | 32000 | 1 |
| `2026-05-25_mmx_first_pass` | `bgm_candy_battle_loop_v001` | `music` | `music/bgm_candy_battle_loop_v001.mp3` | 123.762358 | 44100 | 2 |
| `2026-05-25_mmx_ui_audio_pass` | `voice_level_up_prompt_v001` | `speech` | `audio/voice_level_up_prompt_v001.mp3` | 3.703594 | 32000 | 1 |
| `2026-05-25_mmx_ui_audio_pass` | `jingle_run_settlement_v001` | `music` | `music/jingle_run_settlement_v001.mp3` | 65.027483 | 44100 | 2 |
| `2026-05-26_mmx_level_up_feedback_pack` | `voice_level_up_cn_v001` | `speech` | `audio/voice_level_up_cn_v001.mp3` | 3.494625 | 32000 | 1 |
| `2026-05-26_mmx_level_up_feedback_pack` | `jingle_level_up_v001_source` | `music` | `music/jingle_level_up_v001_source.mp3` | 78.204807 | 44100 | 2 |
| `2026-05-26_mmx_level_up_feedback_pack` | `jingle_level_up_v001_trim3s` | `music` | `processed/audio_v001/jingle_level_up_v001_trim3s.mp3` | 3.2 | 44100 | 2 |
| `2026-05-26_mmx_map_boss_audio_pass` | `voice_boss_arrival_v001` | `speech` | `audio/voice_boss_arrival_v001.mp3` | 2.681906 | 32000 | 1 |
| `2026-05-26_mmx_map_boss_audio_pass` | `sting_boss_arrival_v001` | `music` | `music/sting_boss_arrival_v001.mp3` | 102.42322 | 44100 | 2 |
| `2026-05-26_mmx_map_boss_audio_pass` | `sting_boss_arrival_v001_trim8s` | `music` | `processed/audio_v001/sting_boss_arrival_v001_trim8s.mp3` | 8.0 | 44100 | 2 |
| `2026-05-26_mmx_runtime_topdown_audio_plan` | `voice_boss_arrival_cn_v002` | `speech` | `audio/voice_boss_arrival_cn_v002.mp3` | 3.239188 | 32000 | 1 |
| `2026-05-26_mmx_runtime_topdown_audio_plan` | `sting_boss_arrival_v002_source` | `music` | `music/sting_boss_arrival_v002_source.mp3` | 72.887438 | 44100 | 2 |
| `2026-05-26_mmx_runtime_topdown_audio_plan` | `sting_boss_arrival_v002_trim8s` | `music` | `processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3` | 8.0 | 44100 | 2 |
| `2026-05-26_mmx_runtime_topdown_audio_plan` | `boss_arrival_voice_sting_mix_v001` | `music` | `processed/audio_mix_v001/boss_arrival_voice_sting_mix_v001.mp3` | 8.0 | 44100 | 2 |

## Errors

- None

## Warnings

- None

## Limitations

- This probe checks local file metadata only; it does not judge listening quality, mix balance, clipping by ear, or fatigue.
- A valid technical probe cannot satisfy asset_audio_loudness_review, Runtime preview, final human acceptance, accepted_content, or release gates.
- Non-wav audio requires ffprobe to be available on PATH or passed explicitly.
