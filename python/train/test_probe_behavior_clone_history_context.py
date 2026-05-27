from python.train.probe_behavior_clone_history_context import prefix_indices, score_summary


def test_prefix_indices_returns_requested_history_window():
    indices = [10, 11, 12, 13, 14]

    assert prefix_indices(indices, 13, 2) == [11, 12]
    assert prefix_indices(indices, 10, 3) == []
    assert prefix_indices(indices, 14, 99) == [10, 11, 12, 13]
    assert prefix_indices(indices, 99, 2) == []


def test_score_summary_reports_top_and_action_scores():
    summary = score_summary([0.1, 0.6, 0.3], 3, online_action=2, nearest_action=1)

    assert summary["top_action"] == 1
    assert summary["online_action_score"] == 0.3
    assert summary["nearest_action_score"] == 0.6
