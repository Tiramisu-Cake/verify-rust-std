#!/usr/bin/env python3
"""Isolated evidence-shape controls for the full Linux make-test lane."""
import importlib.util,unittest
from pathlib import Path

path=Path(__file__).with_name('package-evidence.py')
spec=importlib.util.spec_from_file_location('package_evidence',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class FullmakeEvidenceShapeTest(unittest.TestCase):
 def test_exact_affected_captures_are_complete(self):
  payload={name:b'bytes' for name in module.FULLMAKE_CAPTURE_PATHS}
  self.assertEqual(module.missing_case_artifacts('verifast-mdnew-fullmake',payload),[])
 def test_missing_capture_is_incomplete(self):
  payload={name:b'bytes' for name in module.FULLMAKE_CAPTURE_PATHS}
  missing=module.FULLMAKE_CAPTURE_PATHS[-1];del payload[missing]
  self.assertEqual(module.missing_case_artifacts('verifast-mdnew-fullmake',payload),[missing])
 def test_other_lanes_keep_case_requirement(self):
  payload={name:b'bytes' for name in module.FULLMAKE_CAPTURE_PATHS}
  self.assertEqual(module.missing_case_artifacts('verifast-mdnew-cfg',payload),['allprooflogs/cases/*'])
  payload['allprooflogs/cases/forget/source.rs']=b'bytes'
  self.assertEqual(module.missing_case_artifacts('verifast-mdnew-cfg',payload),[])

if __name__=='__main__':unittest.main()
