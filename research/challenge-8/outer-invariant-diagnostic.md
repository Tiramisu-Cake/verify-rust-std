# Qualified outer-loop run: incomplete, unsafe to accept as proof

- Run: https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37390973809
- Source: `a3da2d490ca6129f0abd4c59063b8100ed73981b`
- Selection/budget: `insertion_outer_invariant_4`, 90 minutes.
- Kani pin: `152c6a8c875d9886a67e229247b4826d6105ccfd` (0.67.0), CBMC 6.10.0.
- Domain: initialized four-cell arbitrary i32 array, valid length/offset 1..4,
  fresh arbitrary comparator Boolean per call, no sortedness assumption.
- Qualified macro path compiled; actual safety harness was selected.
- Job ran 23:52:52–00:07:47 UTC (14:55) and stopped with process exit 143
  (SIGTERM). This is neither GNU timeout exit 124 nor a verifier counterexample.
  Selected 90-minute budget and YAML job timeout 150 minutes had not elapsed.
  No cause beyond the signal is reported by job/check-run annotations; do not
  infer OOM or a confirmed platform limit.
- All artifact/post steps were skipped, artifact API reports total_count 0.
  Full job log was fetched locally; no resource artifact survived.

Essential log evidence:

```text
23:58:09 Checking harness ...challenge8_insertion_safety::prove_outer_safety_4
23:58:10 library/kani_core/src/mem.rs:118 same_allocation::<i32>:
  call to ...same_allocation_internal...: not enough arguments,
  inserting non-deterministic value
23:58:10 smallsort.rs:601 invariant closure:
  call to ...ptr::mut_ptr...add...: not enough arguments,
  inserting non-deterministic value
00:05:49 Runtime Symex: 458.716s
00:05:49 size of program expression: 60787 steps
00:05:49 Generated 1244 VCC(s), 828 remaining after simplification
00:07:46 Process completed with exit code 143.
```

These warnings recur during symbolic execution. No final verification summary,
invariant base/step/frame outcomes or seven-cover results were produced.
Even a hypothetical green badge would require resolving the nondeterministic
argument substitutions; they cannot justify a summary of the real functions.

Next: preserve this actual-source reproducer and diagnose the pinned loop
contract/function-call instrumentation before retrying. Do not drop allocation
or bounds obligations to hide the warnings. Independently evaluate the prepared
approved VeriFast exact-source probe for generic/arbitrary-length ownership.
