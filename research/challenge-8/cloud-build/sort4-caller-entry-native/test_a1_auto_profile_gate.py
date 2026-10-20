"""Compatibility entrypoint for the current isolated R6/R7/R8 profile gate."""
import importlib.util
from pathlib import Path
import unittest

TEST_PATH = Path(__file__).with_name("test-a1-focus-profile-binding.py")
SPEC = importlib.util.spec_from_file_location("a1_focus_profile_binding_tests", TEST_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load isolated profile-binding tests")
TESTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TESTS)


class ProfileGateTests(TESTS.FocusProfileBindingTests):
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
