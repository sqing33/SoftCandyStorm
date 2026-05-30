import json
import tempfile
import unittest
from pathlib import Path

from tools.relabel_policy_trace_samples import load_jsonl, relabel_records, write_jsonl


class RelabelPolicyTraceSamplesTests(unittest.TestCase):
    def test_relabels_samples_with_cycled_target_actions(self):
        records = [
            {
                "record_type": "metadata",
                "sample_role": "prefailure_route_diagnostic",
                "sample_source": "source",
            },
            {
                "record_type": "sample",
                "action": 5,
                "observation": [0.1, 0.2],
            },
            {
                "record_type": "sample",
                "action": 5,
                "observation": [0.3, 0.4],
            },
            {
                "record_type": "sample",
                "action": 4,
                "observation": [0.5, 0.6],
            },
        ]

        output, report = relabel_records(
            records,
            target_actions=[7, 3],
            sample_role="counterfactual_repair_input",
            sample_source="seed63402_counterfactual",
            target_source="counterfactual_prefailure_relabel",
            reason="test reason",
        )

        samples = [item for item in output if item["record_type"] == "sample"]
        self.assertEqual([item["action"] for item in samples], [7, 3, 7])
        self.assertEqual([item["original_action"] for item in samples], [5, 5, 4])
        self.assertEqual(report["sample_count"], 3)
        self.assertEqual(report["unchanged_count"], 0)
        self.assertEqual(report["relabeled_action_distribution"]["7"]["count"], 2)
        self.assertEqual(report["relabeled_action_distribution"]["3"]["count"], 1)
        self.assertEqual(output[0]["counterfactual_targets"]["target_actions"], [7, 3])

    def test_write_and_load_jsonl_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            records = [{"record_type": "sample", "action": 7}]
            write_jsonl(records, path)

            self.assertEqual(load_jsonl(path), records)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), records[0])


if __name__ == "__main__":
    unittest.main()
