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
- `2026-05-27 12:14:26.837 Df kernel[0:8f4a8f] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 72776, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 12:14:26.838 Df kernel[0:8f4a90] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 72777, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 12:14:26.838 Df kernel[0:8f4a91] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 72778, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-27 12:14:26.838 Df kernel[0:8f4a92] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 72779, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`

## Next Actions

- Run target/debug/game_harness --help with the same timeout guard.
- If game_harness launches, rerun cargo test --workspace and the blocked Harness/Gym reports.

## Post-Diagnostic Verification

- `target/debug/game_harness --help` returned usage text with exit code 0 under a 5 second timeout guard.
- `cargo test --workspace` passed: 8 bot_policies, 35 game_core, 15 game_harness and 57 game_runtime unit tests, plus doc tests.
- `cargo run -p game_harness -- simulate --seed 12345 --map-id frosting-grassland --seconds 60 --tick-rate 30 --bot kite --content-dir content/base_demo` completed with `terminal = victory`, `reason = duration_reached`, `kills = 46`, `level = 3`, and `damage_taken = 0`.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
