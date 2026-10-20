"""Extracted recovery shell branch; fake stage, no proof or Cloud execution."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent.parent / 'run-o26-refresh.sh'
TEXT = SOURCE.read_text()
START = TEXT.index('if [[ "${LANE:-}" == o26-sort4-c1-current-recovery ]]; then\n')
END = TEXT.index('if [[ "${LANE:-}" == o26-compatible-strict-cut-test ]]', START)
BRANCH = TEXT[START:END]
PREFIX = '''set -euo pipefail
cp() {
  if [[ "$COPY_EXIT" != 0 ]]; then return "$COPY_EXIT"; fi
  command cp "$@"
}
stage() {
  if [[ "$WRITE_AUDIT" == 1 ]]; then
    mkdir -p "$ev/cases/sort4-c1-current-recovery"
    printf '%s' "$AUDIT_BYTES" > "$ev/cases/sort4-c1-current-recovery/diagnostic-audit.json"
  fi
  return "$STAGE_EXIT"
}
'''

class PartialAudit(unittest.TestCase):
    def run_case(self, code, write, copy_exit=0):
        payload = '{"accepted":false,"classification":"PARTIAL","case_status":{"P1":{"status":"INCONCLUSIVE","artifact":null}},"proof_credit":false}\n'
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env = dict(os.environ, LANE='o26-sort4-c1-current-recovery',
                       STAGE_EXIT=str(code), WRITE_AUDIT=str(int(write)), AUDIT_BYTES=payload, COPY_EXIT=str(copy_exit))
            env.update({key: str(root) for key in ('cloud_dir','source_home','stock_home',
                       'compiler_sysroot','proof_root','work_root','ev','evidence_root')})
            env['deadline'] = '0'
            result = subprocess.run(['bash','-ceu',PREFIX+BRANCH], env=env, capture_output=True, text=True)
            output = root / 'proof-audit.json'
            value = output.read_text() if output.exists() else None
        return result, value, payload

    def test_stage_success_and_error_timeout_preserve_identical_partial_audit(self):
        for code in (0,1,124):
            with self.subTest(code=code):
                result, value, original = self.run_case(code, True)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(value, original)
                self.assertFalse(json.loads(value)['accepted'])
                self.assertIsNone(json.loads(value)['case_status']['P1']['artifact'])

    def test_copy_failure_never_masks_original_nonzero_stage_status(self):
        for code in (0,42,124):
            with self.subTest(code=code):
                result, value, _ = self.run_case(code, True, copy_exit=17)
                self.assertEqual(result.returncode, code if code else 1)
                self.assertIsNone(value)
                self.assertIn('diagnostic audit copy failed', result.stderr)

    def test_missing_partial_audit_preserves_original_error(self):
        result, value, _ = self.run_case(42, False)
        self.assertEqual(result.returncode, 42)
        self.assertIsNone(value)

    def test_missing_audit_after_nominal_success_remains_error(self):
        result, value, _ = self.run_case(0, False)
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(value)
        self.assertIn('omitted diagnostic-audit.json', result.stderr)

if __name__ == '__main__': unittest.main()
