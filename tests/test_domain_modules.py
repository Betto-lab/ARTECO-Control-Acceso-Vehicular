import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


def load_module(name):
    path = ROOT / "lambda" / name / "index.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PlateRecognitionTests(unittest.TestCase):
    def test_selects_high_confidence_plate(self):
        module = load_module("plate_recognition")
        result = module.select_plate([
            {"Type": "LINE", "DetectedText": "ABC-123", "Confidence": 96.2}
        ])
        self.assertEqual(result["plate"], "ABC123")

    def test_rejects_low_confidence_text(self):
        module = load_module("plate_recognition")
        self.assertIsNone(module.select_plate([
            {"Type": "LINE", "DetectedText": "ABC-123", "Confidence": 70}
        ]))


class FaceVerificationTests(unittest.TestCase):
    def test_similarity_threshold(self):
        module = load_module("face_verification")
        self.assertTrue(module.is_verified([{"Similarity": 95}]))
        self.assertFalse(module.is_verified([{"Similarity": 89.9}]))


class AccessRegistrationTests(unittest.TestCase):
    def test_event_id_is_stable(self):
        module = load_module("access_registration")
        payload = {"plate": "ABC123", "event_type": "ENTRY", "gate_id": "gate-01", "occurred_at": "2026-11-12T12:00:00Z"}
        self.assertEqual(module.build_access_event(payload)["event_id"], module.build_access_event(payload)["event_id"])


class AlertTests(unittest.TestCase):
    def test_builds_valid_alert(self):
        module = load_module("alerts")
        alert = module.build_alert({"severity": "critical", "message": "Acceso rechazado"})
        self.assertEqual(alert["severity"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
