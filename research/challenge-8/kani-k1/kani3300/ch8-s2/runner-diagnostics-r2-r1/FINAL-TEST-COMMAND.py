# Exact Python unittest recipe executed from stdin for FINAL-32-TESTS.txt.
# Run from the candidate's ch8-s1-control directory. No compiler/full runner.
import unittest
names = [
    'test_rustc_diagnostics', 'test_runner.ExecutionTests',
    'test_runner.CompileTests.test_compile_timeout_missing_wrong_marker_and_process_failures',
    'test_runner.CompileTests.test_live_head_tail_capture_survives_missing_finalization',
    'test_s107.FinalizationTests',
    'test_package.PackageTests.test_fallback_preserves_receipt_materializes_tail_and_bounds',
    'test_package.PackageTests.test_fallback_terminal_after_setup_failure_and_mid_run_interruption',
    'test_package.PackageTests.test_build_wrapper_receipts_and_errors_without_build',
]
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
raise SystemExit(not result.wasSuccessful())
