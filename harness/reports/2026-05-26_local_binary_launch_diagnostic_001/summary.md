# Local Binary Launch Diagnostic

- Decision: `local_binary_launch_blocked`
- Repo root: `/Users/chongqing/Codes/软糖风暴`
- System binary runs: `True`
- Hello compiled: `True`
- Hello runs: `False`
- Hello timed out: `True`
- Developer Mode disabled: `True`
- `spctl` rejected hello: `True`
- `com.apple.provenance` present: `True`
- AMFI no CMS blob signal: `False`
- Security policy denial signal: `True`

## Key Command Output

- Developer Mode: `Developer mode is currently disabled.`
- `spctl --status`: `assessments enabled`
- Hello run elapsed: `5.004` seconds
- Hello run stdout: ``
- Hello run stderr: ``

## Policy Log Signals

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
- `2026-05-26 08:53:10.188 Df kernel[0:42a650] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3826, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:10.188 Df kernel[0:42a651] (AppleSystemPolicy) ASP: Unable to apply provenance sandbox: 268451845, 3827, /Applications/Visual Studio Code.app/Contents/Frameworks/Code Helper (Plugin).app/Contents/MacOS/Code Helper (Plugin)`
- `2026-05-26 08:53:11.141 Df kernel[0:42a5e7] (AppleSystemPolicy) ASP: Security policy would not allow process: 3778, /private/var/folders/b5/2g_p41b51hs3mspctvst_6lr0000gp/T/softcandy_binary_launch_h5hr8rcq/softcandy_hello`

## Next Actions

- Do not treat Harness, Runtime, or Gym timeouts as game logic failures until this diagnostic returns local_binary_launch_ok.
- Run the same diagnostic from a trusted developer host or after enabling Developer Mode for the tool that launches local binaries.
- If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature, then rerun this diagnostic.
- Developer Mode is disabled in this session; enabling it is likely required before local ad-hoc binaries can launch.
- Policy logs show AppleSystemPolicy or AMFI blocking the compiled hello binary before main executes.

## Limitations

- This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.
- It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.
- A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.
