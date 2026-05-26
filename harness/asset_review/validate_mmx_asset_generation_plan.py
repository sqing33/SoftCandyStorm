#!/usr/bin/env python3
"""Validate mmx asset generation plans before running media jobs.

The plan gate checks where generated files would land, which mmx commands would
run, and which follow-up review gates are required. It does not execute mmx and
does not accept any generated asset into Runtime or release content.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


EXPECTED_CONTRACT_ID = "mmx-asset-generation-plan-v0"
ALLOWED_ASSET_TYPES = {"image", "speech", "music"}
COMMAND_BY_TYPE = {
    "image": ("image", "generate"),
    "speech": ("speech", "synthesize"),
    "music": ("music", "generate"),
}
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
    "release_ready": False,
    "requires_metadata_manifest": True,
    "requires_command_provenance": True,
    "requires_human_review": True,
}
REQUIRED_NEXT_CHECKS = {
    "tools/validate_asset_candidates.py",
    "harness/asset_review/create_asset_candidate_review_draft.py",
}
REQUIRED_AGENT_FLAGS = {"--non-interactive", "--quiet"}
TODO_MARKERS = ("TODO", "<", ">")
BANNED_TOKENS = {"--api-key", "--stream"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in TODO_MARKERS)
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside(base_dir: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(base_dir.resolve())
    except ValueError:
        return False
    return True


def require_repo_relative_path(
    repo_root: Path,
    label: str,
    value: Any,
    errors: list[str],
) -> Path | None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be non-empty")
        return None
    if has_placeholder(value):
        errors.append(f"{label} must not contain TODO or placeholder markers")
        return None
    path = Path(str(value))
    if path.is_absolute():
        errors.append(f"{label} must be repository-relative: {value}")
        return None
    resolved = resolve_repo_path(repo_root, str(value))
    if not is_inside(repo_root, resolved):
        errors.append(f"{label} must stay inside repository: {value}")
        return None
    return resolved


def validate_target_batch_path(
    repo_root: Path,
    target_batch_id: str | None,
    target_batch_path: Any,
    errors: list[str],
) -> Path | None:
    target_dir = require_repo_relative_path(repo_root, "target_batch_path", target_batch_path, errors)
    if target_dir is None:
        return None
    generated_root = repo_root / "asset" / "generated_candidates"
    if not is_inside(generated_root, target_dir):
        errors.append("target_batch_path must stay under asset/generated_candidates")
    if target_batch_id and target_dir.name != target_batch_id:
        errors.append("target_batch_id must match target_batch_path directory name")
    return target_dir


def tokens_from_command(value: Any, label: str, errors: list[str]) -> list[str]:
    if isinstance(value, list):
        tokens = []
        for index, token in enumerate(value):
            if not is_nonempty_string(token):
                errors.append(f"{label}[{index}] must be a non-empty string")
                continue
            tokens.append(str(token))
        return tokens
    if is_nonempty_string(value):
        try:
            return shlex.split(str(value))
        except ValueError as error:
            errors.append(f"{label} cannot be parsed as a shell command: {error}")
            return []
    errors.append(f"{label} must be a command string or token list")
    return []


def token_value(tokens: list[str], flag: str) -> str | None:
    prefix = f"{flag}="
    for index, token in enumerate(tokens):
        if token == flag and index + 1 < len(tokens):
            return tokens[index + 1]
        if token.startswith(prefix):
            return token[len(prefix) :]
    return None


def has_flag(tokens: list[str], flag: str) -> bool:
    prefix = f"{flag}="
    return any(token == flag or token.startswith(prefix) for token in tokens)


def output_path_is_inside_target(repo_root: Path, target_dir: Path, value: str) -> bool:
    path = Path(value)
    if path.is_absolute():
        return False
    resolved = resolve_repo_path(repo_root, value)
    return is_inside(target_dir, resolved)


def validate_mmx_command(
    repo_root: Path,
    target_dir: Path | None,
    asset_type: str,
    command: Any,
    label: str,
    errors: list[str],
) -> list[str]:
    tokens = tokens_from_command(command, label, errors)
    if not tokens:
        return tokens

    if has_placeholder(tokens):
        errors.append(f"{label} must not contain TODO or placeholder markers")
    if any(token in BANNED_TOKENS or any(token.startswith(f"{banned}=") for banned in BANNED_TOKENS) for token in tokens):
        errors.append(f"{label} must not use banned flags: {', '.join(sorted(BANNED_TOKENS))}")
    if any(token.startswith("sk-") for token in tokens):
        errors.append(f"{label} must not inline API keys")
    if len(tokens) < 3 or tokens[0] != "mmx":
        errors.append(f"{label} must start with `mmx <category> <action>`")
        return tokens

    expected_category, expected_action = COMMAND_BY_TYPE[asset_type]
    if (tokens[1], tokens[2]) != (expected_category, expected_action):
        errors.append(f"{label} for {asset_type} must use `mmx {expected_category} {expected_action}`")

    missing_flags = sorted(flag for flag in REQUIRED_AGENT_FLAGS if not has_flag(tokens, flag))
    if missing_flags:
        errors.append(f"{label} missing agent flags: {', '.join(missing_flags)}")
    if token_value(tokens, "--output") != "json":
        errors.append(f"{label} must include `--output json`")

    if asset_type == "image":
        if not is_nonempty_string(token_value(tokens, "--prompt")):
            errors.append(f"{label} image command requires --prompt")
        out_dir = token_value(tokens, "--out-dir")
        if not is_nonempty_string(out_dir):
            errors.append(f"{label} image command requires --out-dir")
        elif target_dir is not None and not output_path_is_inside_target(repo_root, target_dir, str(out_dir)):
            errors.append(f"{label} --out-dir must stay inside target_batch_path")
        if not is_nonempty_string(token_value(tokens, "--out-prefix")):
            errors.append(f"{label} image command requires --out-prefix")
    elif asset_type == "speech":
        if not (is_nonempty_string(token_value(tokens, "--text")) or is_nonempty_string(token_value(tokens, "--text-file"))):
            errors.append(f"{label} speech command requires --text or --text-file")
        out_path = token_value(tokens, "--out")
        if not is_nonempty_string(out_path):
            errors.append(f"{label} speech command requires --out")
        elif target_dir is not None and not output_path_is_inside_target(repo_root, target_dir, str(out_path)):
            errors.append(f"{label} --out must stay inside target_batch_path")
    elif asset_type == "music":
        if not is_nonempty_string(token_value(tokens, "--prompt")):
            errors.append(f"{label} music command requires --prompt")
        if not has_flag(tokens, "--instrumental") and not (
            is_nonempty_string(token_value(tokens, "--lyrics")) or is_nonempty_string(token_value(tokens, "--lyrics-file"))
        ):
            errors.append(f"{label} music command requires --instrumental or lyrics")
        out_path = token_value(tokens, "--out")
        if not is_nonempty_string(out_path):
            errors.append(f"{label} music command requires --out")
        elif target_dir is not None and not output_path_is_inside_target(repo_root, target_dir, str(out_path)):
            errors.append(f"{label} --out must stay inside target_batch_path")

    return tokens


def validate_planned_outputs(
    repo_root: Path,
    target_dir: Path | None,
    asset_id: str,
    planned_outputs: Any,
    errors: list[str],
) -> int:
    outputs = string_list(planned_outputs)
    if not outputs:
        errors.append(f"{asset_id}: planned_outputs must be a non-empty list of paths")
        return 0
    for output in outputs:
        if has_placeholder(output):
            errors.append(f"{asset_id}: planned output must not contain TODO or placeholder markers")
            continue
        path = Path(output)
        if path.is_absolute():
            errors.append(f"{asset_id}: planned output must be relative to target_batch_path")
            continue
        if ".." in path.parts:
            errors.append(f"{asset_id}: planned output must not traverse directories: {output}")
        if target_dir is not None:
            resolved = target_dir / path
            if not is_inside(target_dir, resolved):
                errors.append(f"{asset_id}: planned output must stay inside target_batch_path: {output}")
    return len(outputs)


def validate_planned_asset(
    repo_root: Path,
    target_dir: Path | None,
    asset: Any,
    index: int,
    seen_ids: set[str],
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(asset, dict):
        return None, [f"planned_assets[{index}] must be an object"], warnings

    asset_id = asset.get("id")
    display_id = str(asset_id) if is_nonempty_string(asset_id) else f"planned_assets[{index}]"
    if not is_nonempty_string(asset_id):
        errors.append(f"{display_id}: id must be non-empty")
    elif has_placeholder(asset_id):
        errors.append(f"{display_id}: id must not contain TODO or placeholder markers")
    elif str(asset_id) in seen_ids:
        errors.append(f"{display_id}: duplicate planned asset id")
    else:
        seen_ids.add(str(asset_id))

    asset_type = asset.get("type")
    if asset_type not in ALLOWED_ASSET_TYPES:
        errors.append(f"{display_id}: type must be one of {', '.join(sorted(ALLOWED_ASSET_TYPES))}")
        asset_type = "image"
    else:
        asset_type = str(asset_type)

    if not is_nonempty_string(asset.get("purpose")):
        errors.append(f"{display_id}: purpose must be non-empty")
    elif has_placeholder(asset.get("purpose")):
        errors.append(f"{display_id}: purpose must not contain TODO or placeholder markers")

    if asset_type in {"image", "music"}:
        if not is_nonempty_string(asset.get("prompt")):
            errors.append(f"{display_id}: prompt must be non-empty")
        elif has_placeholder(asset.get("prompt")):
            errors.append(f"{display_id}: prompt must not contain TODO or placeholder markers")
    if asset_type == "image":
        if not is_nonempty_string(asset.get("negative_prompt")):
            errors.append(f"{display_id}: image assets require negative_prompt")
    if asset_type == "speech":
        if not is_nonempty_string(asset.get("text")):
            errors.append(f"{display_id}: speech assets require text")
        if not is_nonempty_string(asset.get("voice")):
            errors.append(f"{display_id}: speech assets require voice")

    output_count = validate_planned_outputs(repo_root, target_dir, display_id, asset.get("planned_outputs"), errors)
    command_tokens = validate_mmx_command(repo_root, target_dir, asset_type, asset.get("command"), f"{display_id}.command", errors)

    review_checks = string_list(asset.get("review_focus"))
    if not review_checks:
        warnings.append(f"{display_id}: review_focus should list human review concerns")

    return (
        {
            "id": display_id,
            "type": asset_type,
            "planned_output_count": output_count,
            "command": " ".join(command_tokens),
            "review_focus_count": len(review_checks),
        },
        errors,
        warnings,
    )


def validate_project_rules(payload: dict[str, Any], errors: list[str]) -> None:
    project_rules = payload.get("project_rules")
    if not isinstance(project_rules, dict):
        errors.append("project_rules must be an object")
        return
    for field, expected in REQUIRED_PROJECT_RULES.items():
        if project_rules.get(field) is not expected:
            errors.append(f"project_rules.{field} must be {json.dumps(expected)}")


def validate_post_generation_checks(payload: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    checks = string_list(payload.get("post_generation_checks"))
    if not checks:
        errors.append("post_generation_checks must be a non-empty list")
        return
    if has_placeholder(checks):
        errors.append("post_generation_checks must not contain TODO or placeholder markers")
    missing = sorted(required for required in REQUIRED_NEXT_CHECKS if not any(required in check for check in checks))
    if missing:
        errors.append(f"post_generation_checks missing required checks: {', '.join(missing)}")
    if not any("--require-commands" in check for check in checks):
        warnings.append("post_generation_checks should run validate_asset_candidates.py with --require-commands")


def build_report(plan_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(plan_path)
    repo_root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not is_inside(repo_root, plan_path.resolve()):
        errors.append(f"plan must stay inside repository: {plan_path}")
    if payload.get("plan_contract_id") != EXPECTED_CONTRACT_ID:
        errors.append(f"plan_contract_id must be `{EXPECTED_CONTRACT_ID}`")
    if not isinstance(payload.get("plan_version"), int) or payload["plan_version"] <= 0:
        errors.append("plan_version must be a positive integer")
    for field in ("plan_id", "created_at", "target_batch_id"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")

    generator = payload.get("generator")
    if not isinstance(generator, dict):
        errors.append("generator must be an object")
    elif generator.get("tool") != "mmx-cli":
        errors.append("generator.tool must be `mmx-cli`")

    validate_project_rules(payload, errors)
    target_dir = validate_target_batch_path(
        repo_root,
        str(payload.get("target_batch_id")) if is_nonempty_string(payload.get("target_batch_id")) else None,
        payload.get("target_batch_path"),
        errors,
    )

    assets = payload.get("planned_assets")
    asset_reports: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    if not isinstance(assets, list) or not assets:
        errors.append("planned_assets must be a non-empty list")
        assets = []
    for index, asset in enumerate(assets):
        asset_report, asset_errors, asset_warnings = validate_planned_asset(repo_root, target_dir, asset, index, seen_ids)
        errors.extend(asset_errors)
        warnings.extend(asset_warnings)
        if asset_report is not None:
            asset_reports.append(asset_report)
    if payload.get("asset_count") != len(asset_reports):
        errors.append("asset_count must match planned_assets length")

    validate_post_generation_checks(payload, errors, warnings)
    if payload.get("manual_review_required") is not True:
        errors.append("manual_review_required must be true")
    if has_placeholder(payload.get("notes")):
        errors.append("notes must not contain TODO or placeholder markers")

    return {
        "report_version": 1,
        "source": str(plan_path),
        "repo_root": str(repo_root),
        "decision": "mmx_asset_generation_plan_valid" if not errors else "mmx_asset_generation_plan_invalid",
        "plan_id": payload.get("plan_id"),
        "target_batch_id": payload.get("target_batch_id"),
        "target_batch_path": payload.get("target_batch_path"),
        "asset_count": len(asset_reports),
        "errors": errors,
        "warnings": warnings,
        "planned_assets": asset_reports,
        "limitations": [
            "This validator checks an mmx generation plan only; it does not call mmx or create media files.",
            "A valid plan must still produce metadata manifests, candidate validation reports, postprocess outputs, and human review records before any Runtime candidate promotion.",
            "A valid plan does not mark assets as accepted_content, runtime_integrated, release_ready, or visually/audio approved.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# mmx Asset Generation Plan Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Plan: `{report['plan_id']}`",
        f"- Target batch: `{report['target_batch_id']}`",
        f"- Target path: `{report['target_batch_path']}`",
        f"- Planned assets: {report['asset_count']}",
        "",
        "## Planned Assets",
        "",
        "| Asset | Type | Outputs | Review Focus |",
        "|---|---|---:|---:|",
    ]
    for asset in report["planned_assets"]:
        lines.append(
            f"| `{asset['id']}` | `{asset['type']}` | {asset['planned_output_count']} | {asset['review_focus_count']} |"
        )

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an mmx asset generation plan.")
    parser.add_argument(
        "plan",
        type=Path,
        nargs="?",
        default=Path("harness/asset_review/mmx_asset_generation_plan_template.json"),
        help="mmx generation plan JSON",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.plan, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "mmx_asset_generation_plan_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
