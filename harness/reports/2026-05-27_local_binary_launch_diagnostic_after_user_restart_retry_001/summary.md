# Local Binary Launch Diagnostic

- Decision: `local_binary_launch_ok`
- Repo root: `/Users/chongqing/Codes/软糖风暴`
- System binary runs: `True`
- Hello compiled: `True`
- Hello runs: `True`
- Hello timed out: `False`
- Developer Mode disabled: `False`
- `spctl` rejected hello: `True`
- `com.apple.provenance` present: `True`
- AMFI no CMS blob signal: `False`
- Security policy denial signal: `False`

## Key Command Output

- Developer Mode: `Developer mode is currently enabled.`
- `spctl --status`: `assessments enabled`
- Hello run elapsed: `0.004` seconds
- Hello run stdout: `softcandy-local-binary-ok`
- Hello run stderr: ``

## Policy Log Signals

- `Filtering the log data using "process == "syspolicyd" OR process == "amfid" OR composedMessage CONTAINS[c] "Security policy" OR composedMessage CONTAINS[c] "CMS blob" OR composedMessage CONTAINS[c] "provenance" OR composedMessage CONTAINS[c] "Gatekeeper" OR composedMessage CONTAINS[c] "softcandy""`
- `2026-05-27 09:58:01.353 Df kernel[0:86fd7a] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71263, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 09:58:01.353 Df kernel[0:86fd7b] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71264, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 09:58:01.354 Df kernel[0:86fd7c] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71265, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 09:58:01.354 Df kernel[0:86fd7d] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71266, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 09:58:01.559 Df kernel[0:86fd89] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71268, /Applications/Codex.app/Contents/MacOS/Codex`
- `2026-05-27 09:58:01.560 Df kernel[0:86fd8a] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71269, /Applications/Codex.app/Contents/MacOS/Codex`
- `2026-05-27 09:58:01.561 Df kernel[0:86fd8b] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71270, /Applications/Codex.app/Contents/MacOS/Codex`
- `2026-05-27 09:58:01.561 Df kernel[0:86fd8c] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71271, /Applications/Codex.app/Contents/MacOS/Codex`
- `2026-05-27 09:58:01.561 Df kernel[0:86fd8d] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71272, /Applications/Codex.app/Contents/MacOS/Codex`
- `2026-05-27 09:58:01.561 Df kernel[0:86fd8e] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71273, /Applications/Codex.app/Contents/MacOS/Codex`
- `2026-05-27 09:58:01.562 Df kernel[0:86fd8f] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 71274, /Applications/Codex.app/Contents/MacOS/Codex`

## Next Actions

- Run target/debug/game_harness --help with the same timeout guard.
- If game_harness launches, rerun cargo test --workspace and the blocked Harness/Gym reports.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
