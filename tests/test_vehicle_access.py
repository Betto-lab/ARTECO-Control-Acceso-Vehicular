import importlib.util
import os
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "lambda" / "vehicle_access" / "index.py"
SPEC = importlib.util.spec_from_file_location("vehicle_access", MODULE_PATH)
VEHICLE_ACCESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VEHICLE_ACCESS)


class FakeRdsData:
    def __init__(self, authorized=False):
        self.authorized = authorized
        self.statements = []

    def execute_statement(self, **request):
        self.statements.append(request)
        if request["sql"].startswith("SELECT id, owner_name"):
            if not self.authorized:
                return {"columnMetadata": [], "records": []}
            return {
                "columnMetadata": [{"name": "id"}, {"name": "owner_name"}],
                "records": [[{"longValue": 7}, {"stringValue": "Marielsys"}]],
            }
        return {"columnMetadata": [], "records": []}


class VehicleAccessTests(unittest.TestCase):
    def setUp(self):
        os.environ["DB_CLUSTER_ARN"] = "cluster"
        os.environ["DB_SECRET_ARN"] = "secret"
        VEHICLE_ACCESS._schema_ready = False

    def test_registers_vehicle(self):
        result = VEHICLE_ACCESS.register_vehicle(
            {"plate": "ABC-123", "owner_name": "Marielsys"}, FakeRdsData()
        )
        self.assertEqual(result["plate"], "ABC123")
        self.assertTrue(result["active"])

    def test_persists_and_allows_registered_vehicle(self):
        result = VEHICLE_ACCESS.record_access(
            {"plate": "ABC-123", "event_type": "entry", "gate_id": "gate-01"},
            FakeRdsData(authorized=True),
        )
        self.assertEqual(result["decision"], "ALLOW")
        self.assertTrue(result["persistence_completed"])
        self.assertEqual(result["owner_name"], "Marielsys")

    def test_persists_and_denies_unknown_vehicle(self):
        result = VEHICLE_ACCESS.record_access(
            {"plate": "ZZZ-999", "event_type": "entry", "gate_id": "gate-01"},
            FakeRdsData(authorized=False),
        )
        self.assertEqual(result["decision"], "DENY")
        self.assertTrue(result["persistence_completed"])

    def test_rejects_invalid_payload(self):
        with self.assertRaisesRegex(ValueError, "event_type"):
            VEHICLE_ACCESS.record_access(
                {"plate": "?", "event_type": "visit", "gate_id": ""}, FakeRdsData()
            )


if __name__ == "__main__":
    unittest.main()
