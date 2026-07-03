import os
import unittest

from functions import permissionsFunctions as permissions


class PermissionsFunctionsTest(unittest.TestCase):
    def setUp(self):
        self.original_puid = os.environ.get("PUID")
        self.original_pgid = os.environ.get("PGID")

    def tearDown(self):
        if self.original_puid is None:
            os.environ.pop("PUID", None)
        else:
            os.environ["PUID"] = self.original_puid

        if self.original_pgid is None:
            os.environ.pop("PGID", None)
        else:
            os.environ["PGID"] = self.original_pgid

    def test_configured_ownership_reads_numeric_ids(self):
        os.environ["PUID"] = "1000"
        os.environ["PGID"] = "1001"

        self.assertEqual(permissions.configuredOwnership(), (1000, 1001))

    def test_configured_ownership_ignores_invalid_ids(self):
        os.environ["PUID"] = "not-a-number"
        os.environ["PGID"] = "1001"

        self.assertEqual(permissions.configuredOwnership(), (None, None))


if __name__ == "__main__":
    unittest.main()
