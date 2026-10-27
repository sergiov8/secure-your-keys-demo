"""Offline tests. No credentials, network or Google Cloud project needed."""

import os
import tempfile
import unittest

from bonus_spend_cap.create_spend_cap import ELIGIBLE_SERVICES, build_spend_cap_budget
from common.config import DEFAULT_LOCATION, DEFAULT_MODEL, ConfigError, load_settings
from step1_keyless_auth.scan_for_keys import scan_text, scan_tree
from step3_secret_manager.read_secret import secret_version_name

# Built at runtime so this file never contains a key-shaped string itself.
FAKE_KEY = "AIza" + "X" * 35


class ConfigTest(unittest.TestCase):
    def test_missing_project_raises(self):
        with self.assertRaises(ConfigError):
            load_settings({})

    def test_defaults(self):
        s = load_settings({"GOOGLE_CLOUD_PROJECT": "p"})
        self.assertEqual((s.project, s.location, s.model), ("p", DEFAULT_LOCATION, DEFAULT_MODEL))

    def test_overrides(self):
        s = load_settings(
            {"GOOGLE_CLOUD_PROJECT": "p", "GOOGLE_CLOUD_LOCATION": "europe-west4", "GEMINI_MODEL": "m"}
        )
        self.assertEqual((s.location, s.model), ("europe-west4", "m"))


class ScanForKeysTest(unittest.TestCase):
    def test_finds_google_key(self):
        findings = scan_text(f'KEY = "{FAKE_KEY}"')
        self.assertEqual([f.kind for f in findings], ["google-api-key"])

    def test_finds_literal_api_key_argument(self):
        arg = "api_key"
        findings = scan_text(f'client = genai.Client({arg}="sk-something")')
        self.assertEqual([f.kind for f in findings], ["hardcoded-api-key-argument"])

    def test_ignores_env_lookup(self):
        self.assertEqual(scan_text('genai.Client(api_key=os.environ["GEMINI_API_KEY"])'), [])

    def test_reports_line_numbers_and_skips_venv(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "app.py"), "w") as f:
                f.write(f"ok = 1\nkey = '{FAKE_KEY}'\n")
            os.makedirs(os.path.join(root, ".venv"))
            with open(os.path.join(root, ".venv", "lib.py"), "w") as f:
                f.write(f"key = '{FAKE_KEY}'\n")
            findings = scan_tree(root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 2)


class SpendCapTest(unittest.TestCase):
    def test_body_meets_spend_cap_restrictions(self):
        body = build_spend_cap_budget("my-proj", "agent-platform", 500)
        f = body["budgetFilter"]
        self.assertEqual(f["projects"], ["projects/my-proj"])
        self.assertEqual(f["services"], [f"services/{ELIGIBLE_SERVICES['agent-platform']}"])
        self.assertEqual(f["creditTypesTreatment"], "EXCLUDE_ALL_CREDITS")
        self.assertEqual(f["calendarPeriod"], "MONTH")
        self.assertEqual([r["thresholdPercent"] for r in body["thresholdRules"]], [0.5, 0.8, 1.0])
        self.assertTrue(body["notificationsRule"]["enableProjectLevelRecipients"])
        self.assertEqual(body["spendCap"], {"inputState": "CONFIGURED"})
        self.assertEqual(body["amount"]["specifiedAmount"]["units"], "500")

    def test_rejects_ineligible_service(self):
        with self.assertRaises(ValueError):
            build_spend_cap_budget("p", "bigquery", 100)

    def test_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            build_spend_cap_budget("p", "agent-platform", 0)


class SecretNameTest(unittest.TestCase):
    def test_version_name(self):
        self.assertEqual(
            secret_version_name("p", "stripe-live-key"),
            "projects/p/secrets/stripe-live-key/versions/latest",
        )


if __name__ == "__main__":
    unittest.main()
