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
- Hello run elapsed: `5.003` seconds
- Hello run stdout: ``
- Hello run stderr: ``

## Policy Log Signals

- `Filtering the log data using "process == "syspolicyd" OR process == "amfid" OR composedMessage CONTAINS[c] "Security policy" OR composedMessage CONTAINS[c] "CMS blob" OR composedMessage CONTAINS[c] "provenance" OR composedMessage CONTAINS[c] "Gatekeeper" OR composedMessage CONTAINS[c] "softcandy""`
- `2026-05-26 18:51:18.968 Df kernel[0:5f0e09] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16124, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:18.969 Df kernel[0:5f0e0a] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16125, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:18.969 Df kernel[0:5f0e0b] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16126, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:18.969 Df kernel[0:5f0e0c] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16127, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:21.025 Df kernel[0:5f0e65] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16163, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:21.025 Df kernel[0:5f0e66] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16164, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:21.026 Df kernel[0:5f0e67] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16165, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:21.027 Df kernel[0:5f0e68] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16166, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:23.057 Df kernel[0:5f0ec2] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16176, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:23.058 Df kernel[0:5f0ec3] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16177, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:23.058 Df kernel[0:5f0ec4] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16178, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:23.058 Df kernel[0:5f0ec5] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 16179, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 18:51:23.430 Df kernel[0:5f0dfe] (AppleSystemPolicy) ASP: Security policy would not allow process: 16123, /private/var/folders/b5/2g_p41b51hs3mspctvst_6lr0000gp/T/softcandy_binary_launch_e428hzu2/softcandy_hello`

## Next Actions

- Do not treat Harness, Runtime, or Gym timeouts as game logic failures until this diagnostic returns local_binary_launch_ok.
- Run the same diagnostic from a trusted developer host or after enabling Developer Mode for the tool that launches local binaries.
- If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature, then rerun this diagnostic.
- Policy logs show AppleSystemPolicy or AMFI blocking the compiled hello binary before main executes.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
