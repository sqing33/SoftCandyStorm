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
- Hello run elapsed: `0.003` seconds
- Hello run stdout: `softcandy-local-binary-ok`
- Hello run stderr: ``

## Policy Log Signals

- `Filtering the log data using "process == "syspolicyd" OR process == "amfid" OR composedMessage CONTAINS[c] "Security policy" OR composedMessage CONTAINS[c] "CMS blob" OR composedMessage CONTAINS[c] "provenance" OR composedMessage CONTAINS[c] "Gatekeeper" OR composedMessage CONTAINS[c] "softcandy""`
- `2026-05-26 19:43:41.161 Df kernel[0:61a0a6] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 81371, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 19:43:41.162 Df kernel[0:61a0a7] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 81372, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 19:43:41.162 Df kernel[0:61a0a8] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 81373, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 19:43:41.163 Df kernel[0:61a0a9] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 81374, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`

## Next Actions

- Run target/debug/game_harness --help with the same timeout guard.
- If game_harness launches, rerun cargo test --workspace and the blocked Harness/Gym reports.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
