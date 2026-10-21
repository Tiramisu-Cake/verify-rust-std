"""Small isolated service checks; sparse synthetic files, no real evidence."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("archive_limit", HERE / "package-evidence.py")
PACKAGER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PACKAGER)

class ArchiveLimit(unittest.TestCase):
    def test_complete_compressed_file_limit_is_inclusive_and_lossless(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            archive = out / "evidence.tar.gz"
            for size in (0, PACKAGER.ARCHIVE_MAX_BYTES, PACKAGER.ARCHIVE_MAX_BYTES + 1):
                with archive.open("wb") as stream:
                    stream.truncate(size)
                if size <= PACKAGER.ARCHIVE_MAX_BYTES:
                    PACKAGER.check_archive_size(archive, out)
                else:
                    with self.assertRaises(ValueError):
                        PACKAGER.check_archive_size(archive, out)
                    diagnostic = json.loads((out / "archive-size-failure.json").read_text())
                    self.assertEqual(diagnostic["archive_size_bytes"], size)
                    self.assertEqual(diagnostic["limit_bytes"], 536870912)
                    self.assertIs(diagnostic["artifacts_truncated"], False)
                self.assertEqual(archive.stat().st_size, size)

if __name__ == "__main__":
    unittest.main()
