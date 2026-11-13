# CC1 source/API audit — typecheck NOT_RUN

- rustc_middle::ty::Instance<'tcx> is already copied/converted throughout this
  analysis; the new key retains its full identity and derives Eq/Debug/Copy.
- The single public caller now matches Result<PointsToGraph,PointsToAnalysisError>;
  nested regular calls accept only Ok. No other points-to entry callers exist.
- RefCell is std-only, single-threaded, scoped to one synchronous entry run.
  Callback condition borrows end before nested calls; enter/exit borrows are
  temporary. No RefMut is held across iterate_to_fixpoint or cursor replay.
- Existing Analysis trait signatures/Domain remain unchanged; error is out-of-band
  ONLY inside the root's private dataflow computation and mandatory at its Result
  boundary. Successful graph transfer code and initial_graph handling are intact.
- run's shared references can be reborrowed for each callee's local internal MIR;
  returned graphs only retain the pre-existing tcx lifetime. Actual borrow/type
  compatibility must be checked by the coordinator's pinned compiler.
- MutableBody::from, insert_check(CheckType, SourceInstruction, InsertPosition,
  None, &str) and into follow existing check_values/uninit call sites. Both empty
  and nonempty bb0 select a valid first instruction before insertion.
- BodyTransformation::body populates/reads its cache; the new insert preserves
  all previously transformed/instrumented body content and marks it modified.
- Existing CheckType::UnsupportedCheck uses the established assert/assume-false
  hook, not a new runtime exemption. Its failure must appear in the export.
- Source toolchain remains nightly-2026-10-23. No dependency or toolchain changes.
- Seven Rust helper units and six Rust control files parse with the authorized
  scratchpad rustfmt; that establishes formatting/parser acceptance, not types,
  macro legality, actual capture layout or compiler/verifier behavior.
- 270 protected existing files and all8 oracle input hashes are unchanged;
  STATIC-CHECKS.json records source checks. Python oracle checker:21/21 PASS.
