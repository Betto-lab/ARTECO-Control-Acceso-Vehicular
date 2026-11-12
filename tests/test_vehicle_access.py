import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "lambda" / "vehicle_access" / "index.py"
SPEC = importlib.util.spec_from_file_location("vehicle_access", MODULE_PATH)
VEHICLE_ACCESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VEHICLE_ACCESS)


class VehicleAccessTests(unittest.TestCase):
    def test_accepts_valid_entry_as_prototype(self):
        response = VEHICLE_ACCESS.lambda_handler(
            {"body": json.dumps({"plate": "ABC-123", "event_type": "entry", "gate_id": "gate-01"})},
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 202)
        self.assertEqual(body["plate"], "ABC123")
        self.assertFalse(body["authorization_checked"])
        self.assertFalse(body["persistence_completed"])

    def test_rejects_invalid_payload(self):
        response = VEHICLE_ACCESS.lambda_handler(
            {"body": json.dumps({"plate": "?", "event_type": "visit", "gate_id": ""})},
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 422)
        self.assertEqual(len(body["errors"]), 3)


if __name__ == "__main__":
    unittest.main()
