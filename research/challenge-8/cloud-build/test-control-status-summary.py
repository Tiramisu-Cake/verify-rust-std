"""Synthetic metadata-only tests for bounded Cloud Build status summaries."""
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("status_summary_control", HERE / "control.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load Cloud Build control module")
CONTROL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTROL)


class StatusSummaryTests(unittest.TestCase):
    def test_includes_failure_and_step_status_without_commands_or_environment(self):
        build = {
            "id": "build-123",
            "status": "FAILURE",
            "createTime": "created",
            "startTime": "started",
            "finishTime": "finished",
            "logUrl": "https://example.invalid/logs",
            "failureInfo": {"type": "USER_BUILD_STEP", "detail": "step exited"},
            "steps": [{
                "id": "verify",
                "status": "FAILURE",
                "exitCode": 17,
                "timing": {"startTime": "step-start", "endTime": "step-end"},
                "args": ["secret-command"],
                "env": ["TOKEN=secret"],
                "name": "private-image-reference",
            }],
            "substitutions": {"SECRET": "do-not-print"},
            "options": {"env": ["BUILD_SECRET=x"]},
        }
        summary = CONTROL.status_summary(build)
        self.assertEqual(set(summary), {
            "id", "status", "createTime", "startTime", "finishTime", "logUrl",
            "failureInfo", "steps",
        })
        self.assertEqual(summary["failureInfo"], build["failureInfo"])
        self.assertEqual(summary["steps"], [{
            "id": "verify",
            "status": "FAILURE",
            "exitCode": 17,
            "timing": {"startTime": "step-start", "endTime": "step-end"},
        }])
        rendered = repr(summary)
        for forbidden in ("secret-command", "TOKEN=secret", "private-image-reference",
                          "do-not-print", "BUILD_SECRET"):
            self.assertNotIn(forbidden, rendered)

    def test_missing_null_and_partial_metadata_have_stable_defaults(self):
        empty = CONTROL.status_summary({})
        self.assertEqual(empty, {
            "id": None, "status": None, "createTime": None, "startTime": None,
            "finishTime": None, "logUrl": None, "failureInfo": None, "steps": [],
        })
        self.assertEqual(CONTROL.status_summary(None), empty)
        partial = CONTROL.status_summary({
            "status": None,
            "failureInfo": None,
            "steps": [None, "bad-shape", {"status": None}],
        })
        self.assertIsNone(partial["status"])
        self.assertIsNone(partial["failureInfo"])
        self.assertEqual(partial["steps"], [{
            "id": None, "status": None, "exitCode": None, "timing": None,
        }])
        self.assertEqual(CONTROL.status_summary({"steps": None})["steps"], [])
        self.assertEqual(CONTROL.status_summary({"steps": {"status": "FAILURE"}})["steps"], [])


if __name__ == "__main__":
    unittest.main()
