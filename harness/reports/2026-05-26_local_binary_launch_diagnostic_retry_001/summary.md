# Local Binary Launch Diagnostic

- Decision: `local_binary_launch_blocked`
- Repo root: `/Users/chongqing/Codes/软糖风暴`
- System binary runs: `True`
- Hello compiled: `True`
- Hello runs: `False`
- Hello timed out: `True`
- Developer Mode disabled: `False`
- `spctl` rejected hello: `True`
- `com.apple.provenance` present: `True`
- AMFI no CMS blob signal: `False`
- Security policy denial signal: `True`

## Key Command Output

- Developer Mode: `Developer mode is currently enabled.`
- `spctl --status`: `assessments enabled`
- Hello run elapsed: `5.009` seconds
- Hello run stdout: ``
- Hello run stderr: ``

## Policy Log Signals

- `Filtering the log data using "process == "syspolicyd" OR process == "amfid" OR composedMessage CONTAINS[c] "Security policy" OR composedMessage CONTAINS[c] "CMS blob" OR composedMessage CONTAINS[c] "provenance" OR composedMessage CONTAINS[c] "Gatekeeper" OR composedMessage CONTAINS[c] "softcandy""`
- `2026-05-26 18:42:31.443 Df kernel[0:5e8dd0] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5007, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:31.444 Df kernel[0:5e8dd1] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5008, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:31.445 Df kernel[0:5e8dd2] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5009, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:31.446 Df kernel[0:5e8dd3] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5010, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:33.683 Df kernel[0:5e8dff] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5022, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:33.684 Df kernel[0:5e8e00] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5023, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:33.684 Df kernel[0:5e8e01] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5024, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:33.685 Df kernel[0:5e8e02] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5025, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:35.814 Df kernel[0:5e8e49] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5040, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:35.814 Df kernel[0:5e8e4a] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5041, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:35.815 Df kernel[0:5e8e4b] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5042, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:35.815 Df kernel[0:5e8e4c] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 5043, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:42:36.301 Df kernel[0:5e8dcd] (AppleSystemPolicy) ASP: Security policy would not allow process: 5006, /private/var/folders/b5/2g_p41b51hs3mspctvst_6lr0000gp/T/softcandy_binary_launch_3132_oor/softcandy_hello`

## Next Actions

- Do not treat Harness, Runtime, or Gym timeouts as game logic failures until this diagnostic returns local_binary_launch_ok.
- Run the same diagnostic from a trusted developer host or after enabling Developer Mode for the tool that launches local binaries.
- If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature, then rerun this diagnostic.
- Policy logs show AppleSystemPolicy or AMFI blocking the compiled hello binary before main executes.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
