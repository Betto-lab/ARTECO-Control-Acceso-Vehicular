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

    def test_rejects_invalid_owner_without_database_calls(self):
        for owner in (None, 123, True, [], {}, "", "   ", "a" * 121):
            with self.subTest(owner=owner):
                db = FakeRdsData()
                with self.assertRaisesRegex(ValueError, "owner_name"):
                    VEHICLE_ACCESS.register_vehicle(
                        {"plate": "ABC123", "owner_name": owner}, db
                    )
                self.assertEqual(db.statements, [])

    def test_rejects_missing_owner(self):
        db = FakeRdsData()
        with self.assertRaisesRegex(ValueError, "owner_name"):
            VEHICLE_ACCESS.register_vehicle({"plate": "ABC123"}, db)
        self.assertEqual(db.statements, [])

    def test_history_filters_by_normalized_plate(self):
        db = FakeRdsData()
        VEHICLE_ACCESS.list_events(db, "abc-123")
        query = db.statements[-1]
        self.assertIn("WHERE plate = :plate", query["sql"])
        self.assertEqual(query["parameters"], [{"name": "plate", "value": {"stringValue": "ABC123"}}])

    def test_history_rejects_invalid_plate_before_database_call(self):
        db = FakeRdsData()
        with self.assertRaisesRegex(ValueError, "plate"):
            VEHICLE_ACCESS.list_events(db, "abc%' OR 1=1")
        self.assertEqual(db.statements, [])

    def test_owner_boundaries_and_trimming_are_persisted(self):
        for owner in ("A", "a" * 120, "María José"):
            with self.subTest(owner=owner):
                db = FakeRdsData()
                result = VEHICLE_ACCESS.register_vehicle(
                    {"plate": "ABC123", "owner_name": "  " + owner + "  "}, db
                )
                self.assertEqual(result["owner_name"], owner)
                parameters = db.statements[-1]["parameters"]
                saved = next(p for p in parameters if p["name"] == "owner")
                self.assertEqual(saved["value"]["stringValue"], owner)

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
