# Runtime Privacy Settings Contract Validation

- Source: `harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json`
- Policy: `harness/telemetry_privacy/telemetry_privacy_policy_template.json`
- Save contract: `harness/save_contract/save_state_v0_template.json`
- Decision: `runtime_privacy_settings_contract_valid`

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks the expected Runtime settings UI contract only.
- It does not prove Bevy Runtime has implemented the settings screen, persistence, deletion, export, or upload transport.
- Release still requires manual privacy review and executable Runtime verification.
