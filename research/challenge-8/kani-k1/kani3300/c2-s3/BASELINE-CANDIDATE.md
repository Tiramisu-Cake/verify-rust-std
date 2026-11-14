# S3 distinguishing pairs — NOT_RUN

Both pairs are pending coordinator execution. No local cargo/rustc/Kani/CBMC/
Miri/build, baseline run, candidate run, push or CI was performed.

| Control | Exact baseline + test-only package: required | Candidate with identical tests: required | Actual |
| --- | --- | --- | --- |
| repeated-destination | False VERIFICATION SUCCESSFUL; expected-negative compiletest fails | Intended second-return payload read fails | Both NOT_RUN; discrimination UNKNOWN |
| moved-from-source | False VERIFICATION SUCCESSFUL; expected-negative compiletest fails | Intended saved-pointer old-source payload read fails | Both NOT_RUN; discrimination UNKNOWN |
| reinit-companion | Legal payload writes/readbacks | Legal payload writes/readbacks; reset must not erase later reinit | Both NOT_RUN |

The baseline must be bf8170b28afb682f8dd55a94199caa247736d8fa plus only the
separate test-only patch. Patch SHA256, expected tree and file hashes are in
INPUTS.json. Candidate uses byte-identical test sources/goldens/flags.

Require actual consumed MIR bindings: same Call destination local/place on both
returns; source object's saved address before actual Operand::Move; source
storage still allocated; no temporary substituted; aggregate built/returned by
fields without whole-value assignment; #[repr(C)] Nested payload offset 0,
size/align 1, Nested extent 2; retained target read; exact normal-edge/before-call
reset ordering. Layout numbers are Rust source expectations, not measured CI
bindings. A local source file or exact coordinate alone does not establish them.

Failure or Unsupported on baseline, compile failure, removed read, unknown
lowering, different source storage, or nondiscriminating pair is not F6
reproduction. Stop admission and return a corrected bounded test-only request.
Candidate failure must bind only to the intended read and the provisional exact
count/descriptions in CONTROL-MANIFEST. Do not auto-bless other failures or
update goldens from a blanket FAILED result.

All actual inventories, verifier exits, property counts, source-to-MIR bindings,
normal-edge runtime observations, two-pair reproduction and F6 repair acceptance
are NOT_RUN/UNKNOWN. B1/B2/independent proof credit: NONE.
