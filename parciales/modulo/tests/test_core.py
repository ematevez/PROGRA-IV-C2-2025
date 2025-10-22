import unittest
import os

class TestCoreSystem(unittest.TestCase):
    def test_core_exists(self):
        self.assertTrue(os.path.exists("core.py"))

    def test_config_valid(self):
        import json
        with open("config.json") as f:
            cfg = json.load(f)
        self.assertIn("intervalo_automejora", cfg)
        self.assertIn("modelos", cfg)

    def test_backup_folder(self):
        if not os.path.exists("backups"):
            os.makedirs("backups")
        self.assertTrue(os.path.isdir("backups"))
