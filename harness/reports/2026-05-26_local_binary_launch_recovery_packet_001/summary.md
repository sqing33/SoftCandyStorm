# Local Binary Launch Recovery Packet

- Decision: `recovery_required`
- Diagnostic decision: `local_binary_launch_blocked`
- Diagnostic report: `harness/reports/2026-05-26_local_binary_launch_diagnostic_001/local_binary_launch_diagnostic.json`
- Failure case: `harness/failed_cases/fail_20260526_024_local_binary_launch_blocked.json`
- Progress ledger: `harness/progress.json`
- Docs coverage ledger: `harness/docs_implementation_coverage.json`

## Current Signals

| Signal | Value |
|---|---|
| System binary runs | `True` |
| Minimal hello compiled | `True` |
| Minimal hello runs | `False` |
| Minimal hello timed out | `True` |
| Developer Mode disabled | `True` |
| spctl rejected hello | `True` |
| com.apple.provenance present | `True` |
| AMFI no CMS blob signal | `False` |
| Security policy denial signal | `True` |

## Key Checks

| Check | Return code | Timed out | Elapsed seconds | Output |
|---|---:|---|---:|---|
| `system_echo` | `0` | `False` | `0.002` | `system-binary-ok` |
| `developer_mode` | `0` | `False` | `0.007` | `Developer mode is currently disabled.` |
| `spctl_status` | `0` | `False` | `0.004` | `assessments enabled` |
| `cc_compile` | `0` | `False` | `0.05` | `` |
| `spctl_assess` | `3` | `False` | `0.11` | `/var/folders/b5/2g_p41b51hs3mspctvst_6lr0000gp/T/softcandy_binary_launch_h5hr8rcq/softcandy_hello: rejected` |
| `hello_run` | `None` | `True` | `5.004` | `` |

## Policy Log Highlights

- `2026-05-26 08:53:11.141 Df kernel[0:42a5e7] (AppleSystemPolicy) ASP: Security policy would not allow process: 3778, /private/var/folders/b5/2g_p41b51hs3mspctvst_6lr0000gp/T/softcandy_binary_launch_h5hr8rcq/softcandy_hello`
- `Filtering the log data using "process == "syspolicyd" OR process == "amfid" OR composedMessage CONTAINS[c] "Security policy" OR composedMessage CONTAINS[c] "CMS blob" OR composedMessage CONTAINS[c] "provenance" OR composedMessage CONTAINS[c] "Gatekeeper" OR composedMessage CONTAINS[c] "softcandy""`
- `2026-05-26 08:53:06.104 Df kernel[0:42a5d6] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3773, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:06.104 Df kernel[0:42a5d7] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3774, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:06.105 Df kernel[0:42a5d8] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3775, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:06.105 Df kernel[0:42a5d9] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3776, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:08.138 Df kernel[0:42a5f1] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3779, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:08.138 Df kernel[0:42a5f2] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3780, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:08.138 Df kernel[0:42a5f3] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3781, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:08.138 Df kernel[0:42a5f4] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3782, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:10.187 Df kernel[0:42a64e] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3824, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:10.187 Df kernel[0:42a64f] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3825, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`

## Failure Case

- Case id: `fail_20260526_024`
- Category: `tooling`
- Content id: `local_macho_binary_launch`
- Symptom: 本机新生成 Mach-O 可执行文件启动后无输出且不进入 main，Rust game_harness、rustc hello 和 cc hello 均会卡住，导致 game_harness gym-bridge 不能可靠响应
- Root cause: macOS policy 对本地新生成二进制返回 rejected，进程采样停在 _dyld_start；最新诊断显示当前 Developer Mode 为 disabled，最小 cc hello 可编译但 5 秒超时，策略日志出现 AppleSystemPolicy 拒绝本地进程，说明问题集中在当前会话的本地 Mach-O 执行策略而非仓库代码
- Fix: 先恢复本地新编译二进制的启动能力，例如为当前开发宿主启用 Developer Mode，或使用能产生 CMS 签名的可信 code-signing identity；恢复后再重跑 Harness、Runtime 和 Gym 对比。在恢复前不要把依赖 game_harness 的评估失败误判为策略或 GameCore 失败
- Validation: 先运行 tools/diagnose_local_binary_launch.py 并得到 local_binary_launch_ok；再运行 spctl -a -vv target/debug/game_harness、target/debug/game_harness --help、cargo test --workspace；恢复后重跑 context3 behavior clone 60/300 秒 high-pressure 对比

## Why This Is Not Gameplay Evidence

- The compiled hello probe is independent of GameCore, Harness, Runtime, Gym, content, and replay logic.
- The probe compiles successfully but does not enter main before the timeout, so downstream binary timeouts are host execution-policy evidence first.
- Until the diagnostic returns local_binary_launch_ok, Rust/Bevy/Harness/Gym timeouts must remain blocker evidence rather than gameplay or policy-quality evidence.
- Policy logs include a Security policy denial for the newly compiled hello binary.
- Developer Mode is currently disabled in the captured session.

## Recovery Actions

- Enable Developer Mode for the host/toolchain session, or rerun from a trusted developer host.
- If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature.
- Rerun the diagnostic until its decision is exactly local_binary_launch_ok before interpreting game binaries.
- Only after local_binary_launch_ok should Harness, Runtime, Gym, Replay, and RC gates be revalidated.

## Ordered Post-Recovery Validation

1. `python3 tools/diagnose_local_binary_launch.py --repo-root . --report harness/reports/<report-id>/local_binary_launch_diagnostic.json --markdown harness/reports/<report-id>/summary.md --timeout 5`
2. `spctl -a -vv target/debug/game_harness`
3. `target/debug/game_harness --help`
4. `cargo fmt --check`
5. `cargo clippy --workspace --all-targets`
6. `cargo test --workspace`
7. `target/debug/game_harness simulate --bot kite --seed 12345 --seconds 300 --out harness/reports/<report-id>`
8. `target/debug/game_harness matrix --bots all --seed-start <seed> --seeds <count> --seconds 300 --out harness/reports/<report-id>`
9. `target/debug/game_harness replay-batch --input harness/reports/<baseline-replay-dir> --out harness/reports/<report-id>`
10. `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --behavior-clone-model <context3-model> --compare-rule-bots --compare-map-preset high-pressure --eval-seconds 60 --report harness/reports/<report-id>/run_output.json`
11. `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --behavior-clone-model <context3-model> --compare-rule-bots --compare-map-preset high-pressure --eval-seconds 300 --report harness/reports/<report-id>/run_output.json`

## Blocked Docs

| Doc | Status | Blocked items |
|---|---|---:|
| `docs/02_核心玩法规格.md` | `partial` | 1 |
| `docs/06_Bevy技术架构计划.md` | `partial` | 1 |
| `docs/07_Harness工程计划.md` | `partial` | 1 |
| `docs/08_Bot测试计划.md` | `partial` | 1 |
| `docs/09_AI_Bot训练计划.md` | `partial` | 1 |
| `docs/11_测试指标与上线门禁.md` | `partial` | 1 |
| `docs/14_GameCore接口规格.md` | `partial` | 1 |
| `docs/15_经济与数值平衡模型.md` | `partial` | 1 |
| `docs/16_Replay与遥测设计.md` | `partial` | 1 |
| `docs/18_完整游戏流程与局外成长.md` | `partial` | 1 |

## Progress Entries

| Section | Id | Report |
|---|---|---|
| `current_findings` | `local_binary_launch_blocked` | `harness/reports/2026-05-26_local_binary_launch_diagnostic_001/summary.md` |
| `next_recommended` | `local_binary_launch_recovery` | `` |

## Limitations

- This packet organizes recovery evidence only; it does not change host security policy.
- This packet is not gameplay evidence and cannot explain policy quality, balance, or player experience.
- It does not prove Rust, Bevy, GameCore, Harness, Runtime, Gym, Replay, performance, or release gates are working.
- It must not be cited as a passing RC, platform, privacy, legal, or manual playtest gate.
- The blocker remains active until a fresh diagnostic report records local_binary_launch_ok.
