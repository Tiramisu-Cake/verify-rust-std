# Coordinator follow-up request — NOT_RUN, no dispatch authorization

Use exact identities in INPUTS.json. The old two runs are NONDISCRIMINATING;
do not count them as reached target reads or F6 proof pairs.

1. Baseline exact bf8170b28 + this directory's baseline-tests.patch, expected
   tree `1356cb004836d69fa0c234801e9c0600a7146167`. Verify hashes and run both
   negatives separately. Each must give false VERIFICATION SUCCESSFUL, making
   its expected-negative selector fail. Also run the legal reinit companion.
2. Candidate `5ca3cbf2e913e9c9b1d81cad3bce598964bafeac` has byte-identical
   sources/oracles/flags. Require one failed property per negative:
   the exact uninitialized-pointer description for `*const u8` in the .expected
   file, at read_payload's direct load; reinit requires zero failures
   and both equality assertions successful. No extra Unsupported, frame,
   validity, lifetime or address-formation failure is accepted.
3. Bind actual consumed MIR: direct u8 field pointers formed before Call;
   both returns to the same Nested destination; actual Move(source) and retained
   old-source address with live storage; no hidden layout-changing pointer cast
   or copy seed selecting the whole aggregate; retained target read; candidate
   source reset after snapshots/before Call and destination reset on normal edge;
   reinit setters after reset. Test source coordinates alone do not prove this.
4. Preserve the original per-fixture 12-bit flags and normal checks. No expected
   regeneration or check disabling. If baseline fails or candidate hits the old
   guard, classify NONDISCRIMINATING/UNREPRODUCED and return exact bindings for a
   corrected bounded request. Actual new results and failure counts are UNKNOWN.

No production/docs change is included. Existing reported passing suites are
not rerun by the worker. Composition remains the separately recorded S5 debt;
this request grants no blanket waiver for new drift or proof credit.
