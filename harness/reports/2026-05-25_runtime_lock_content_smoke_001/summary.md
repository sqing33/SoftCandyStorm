# Runtime Locked Content Smoke Summary

- Command: `game_runtime --accepted-lock-file <tmp>/accepted_content.lock.json --seconds 1 --demo-input --simulation-speed 16 --auto-exit-after-report`
- Result: Runtime resolved `content/base_demo` from a temporary accepted-content lockfile.
- Content pack id: `base-demo-lock-smoke`
- Final terminal: `victory` by `duration_reached`
- Note: The lockfile used in this smoke was temporary and synthetic. It only verifies Runtime selection from a locked entry; it is not a real human acceptance record.
