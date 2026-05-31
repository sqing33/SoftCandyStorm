import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from validate_terminal_conversion_probe import build_report


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def comparison(win_rate, survival, terminal_decisions=10, terminal_ratio=0.1):
    return {
        "summary": {
            "maps": [
                {
                    "map_id": "caramel-workshop",
                    "policy_win_rate": win_rate,
                    "policy_average_survival_seconds": survival,
                }
            ]
        },
        "maps": [
            {
                "map_id": "caramel-workshop",
                "policy": {
                    "summary": {
                        "win_rate": win_rate,
                        "average_survival_seconds": survival,
                    },
                    "policy_adapter": {
                        "mode": "late_recovery_filter",
                        "wrapped_policy_adapter": {
                            "mode": "terminal_conversion_branch",
                            "usage": {
                                "by_map": {
                                    "caramel-workshop": {
                                        "total_decisions": 100,
                                        "terminal_decisions": terminal_decisions,
                                        "terminal_ratio": terminal_ratio,
                                    }
                                },
                                "by_time_bucket": {
                                    "late_180_to_300": {
                                        "total_decisions": 40,
                                        "terminal_decisions": terminal_decisions,
                                        "terminal_ratio": terminal_ratio,
                                    }
                                },
                            },
                        },
                    },
                },
            }
        ],
    }


def regression(decision="policy_window_regression_passed"):
    return {
        "decision": decision,
        "blockers": [] if decision == "policy_window_regression_passed" else ["regression"],
    }


def test_terminal_conversion_probe_passes_limited_followup(tmp_path):
    baseline = write_json(tmp_path / "baseline.json", comparison(0.0, 220.0, 0, 0.0))
    candidate = write_json(tmp_path / "candidate.json", comparison(0.3333, 245.0, 12, 0.12))
    window_regression = write_json(tmp_path / "regression.json", regression())

    report = build_report(
        baseline_windows={"300s": baseline},
        candidate_windows={"300s": candidate},
        target_map="caramel-workshop",
        target_window="300s",
        terminal_time_bucket="late_180_to_300",
        min_target_win_rate=0.3333,
        min_win_rate_delta=0.3333,
        min_survival_delta=5.0,
        min_terminal_decisions=1,
        min_terminal_ratio=0.01,
        min_bucket_terminal_decisions=1,
        min_bucket_terminal_ratio=0.01,
        window_regression=window_regression,
    )

    assert report["decision"] == "terminal_conversion_probe_passed_for_limited_followup"
    assert report["terminal_usage"]["bucket_terminal_decisions"] == 12
    assert report["target_metrics"]["win_rate_delta"] == 0.3333


def test_terminal_conversion_probe_fails_when_used_without_conversion(tmp_path):
    baseline = write_json(tmp_path / "baseline.json", comparison(0.0, 231.2871, 0, 0.0))
    candidate = write_json(tmp_path / "candidate.json", comparison(0.0, 230.8648, 8, 0.04))
    window_regression = write_json(tmp_path / "regression.json", regression("policy_window_regression_failed"))

    report = build_report(
        baseline_windows={"300s": baseline},
        candidate_windows={"300s": candidate},
        target_map="caramel-workshop",
        target_window="300s",
        terminal_time_bucket="late_180_to_300",
        min_target_win_rate=0.3333,
        min_win_rate_delta=0.3333,
        min_survival_delta=0.0,
        min_terminal_decisions=1,
        min_terminal_ratio=0.01,
        min_bucket_terminal_decisions=1,
        min_bucket_terminal_ratio=0.01,
        window_regression=window_regression,
    )

    assert report["decision"] == "terminal_conversion_probe_failed"
    assert any("win_rate" in blocker for blocker in report["blockers"])
    assert any("window_regression" in blocker for blocker in report["blockers"])
    assert report["warnings"] == [
        "300s/caramel-workshop: terminal branch was used but produced no victories"
    ]


def test_terminal_conversion_probe_invalid_when_target_map_missing(tmp_path):
    baseline = write_json(tmp_path / "baseline.json", {"summary": {"maps": []}})
    candidate = write_json(tmp_path / "candidate.json", {"summary": {"maps": []}})

    report = build_report(
        baseline_windows={"300s": baseline},
        candidate_windows={"300s": candidate},
        target_map="caramel-workshop",
        target_window="300s",
        terminal_time_bucket="late_180_to_300",
        min_target_win_rate=None,
        min_win_rate_delta=0.0,
        min_survival_delta=0.0,
        min_terminal_decisions=1,
        min_terminal_ratio=0.0,
        min_bucket_terminal_decisions=None,
        min_bucket_terminal_ratio=None,
        window_regression=None,
    )

    assert report["decision"] == "terminal_conversion_probe_invalid"
    assert any("target map" in error for error in report["errors"])
