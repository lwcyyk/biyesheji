import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "generate_api_coverage.py"
SPEC = importlib.util.spec_from_file_location("generate_api_coverage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class APICoverageTest(unittest.TestCase):
    def test_all_openapi_operations_are_accounted_for(self):
        report = MODULE.generate()
        self.assertEqual(report["contractVersion"], "2.1.0")
        self.assertEqual(report["operationCount"], 23)
        self.assertTrue(report["allOperationsAccountedFor"])
        self.assertNotIn("UNVERIFIED", report["counts"])

    def test_optional_modules_are_not_reported_complete(self):
        report = MODULE.generate()
        statuses = {
            item["operationId"]: item["status"]
            for item in report["operations"]
        }
        self.assertEqual(statuses["createExposureAnalysis"], "NOT_IMPLEMENTED")
        self.assertEqual(statuses["createRemediationCampaign"], "NOT_IMPLEMENTED")
        self.assertEqual(statuses["createStateResolution"], "PARTIAL")
        self.assertEqual(statuses["createLegacyVdnsResolution"], "PARTIAL")


if __name__ == "__main__":
    unittest.main()
