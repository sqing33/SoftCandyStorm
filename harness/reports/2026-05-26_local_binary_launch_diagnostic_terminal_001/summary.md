# Local Binary Launch Diagnostic

- Decision: `local_binary_launch_blocked`
- Repo root: `/Users/chongqing/Codes/软糖风暴`
- System binary runs: `True`
- Hello compiled: `True`
- Hello runs: `False`
- Hello timed out: `True`
- Developer Mode disabled: `False`
- `spctl` rejected hello: `True`
- `com.apple.provenance` present: `False`
- AMFI no CMS blob signal: `False`
- Security policy denial signal: `True`

## Key Command Output

- Developer Mode: `Developer mode is currently enabled.`
- `spctl --status`: `assessments enabled`
- Hello run elapsed: `5.003` seconds
- Hello run stdout: ``
- Hello run stderr: ``

## Policy Log Signals

- `Filtering the log data using "process == "syspolicyd" OR process == "amfid" OR composedMessage CONTAINS[c] "Security policy" OR composedMessage CONTAINS[c] "CMS blob" OR composedMessage CONTAINS[c] "provenance" OR composedMessage CONTAINS[c] "Gatekeeper" OR composedMessage CONTAINS[c] "softcandy""`
- `2026-05-26 18:52:22.426 Df kernel[0:5f2136] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17664, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:22.426 Df kernel[0:5f2137] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17665, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:22.426 Df kernel[0:5f2138] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17666, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:22.426 Df kernel[0:5f2139] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17667, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:24.460 Df kernel[0:5f2178] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17680, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:24.461 Df kernel[0:5f2179] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17681, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:24.462 Df kernel[0:5f217a] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17682, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:24.463 Df kernel[0:5f217b] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17683, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:26.539 Df kernel[0:5f21a4] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17695, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:26.540 Df kernel[0:5f21a5] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17696, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:26.540 Df kernel[0:5f21a6] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17697, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:26.540 Df kernel[0:5f21a7] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17698, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:28.094 Df kernel[0:5f214a] (AppleSystemPolicy) ASP: Security policy would not allow process: 17669, /private/var/folders/b5/2g_p41b51hs3mspctvst_6lr0000gp/T/softcandy_binary_launch_qxzruaa0/softcandy_hello`
- `2026-05-26 18:52:28.573 Df kernel[0:5f21c6] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17707, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:28.575 Df kernel[0:5f21c7] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17708, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:28.577 Df kernel[0:5f21c8] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17709, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:52:28.581 Df kernel[0:5f21c9] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 17710, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`

## Next Actions

- Do not treat Harness, Runtime, or Gym timeouts as game logic failures until this diagnostic returns local_binary_launch_ok.
- Run the same diagnostic from a trusted developer host or after enabling Developer Mode for the tool that launches local binaries.
- If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature, then rerun this diagnostic.
- Policy logs show AppleSystemPolicy or AMFI blocking the compiled hello binary before main executes.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
