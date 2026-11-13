# Read-only Rust and collector API audit

Rust compilation/typechecking and verification: NOT_RUN. Scratchpad rustfmt is syntax/formatting
only. Marker diagnostics remain [deferred](REQUIRED-STATE.md); no compiler API was changed.

- `relay`: MaybeUninit<u8> by value → same type by value. Both constructors are valid values;
  generic inference is constrained by `input`'s explicit return type. No Arbitrary(MU) implementation
  or any_modifies behavior was edited.
- `payload_is_42`: &MaybeUninit<u8> → bool via existing stable unsafe `assume_init_read`, returning
  Copy u8. Requires/ensures and harness reads are guarded by initialized=true. In actual source
  execution that flag chooses new(42); the uninit-storage branch does not form an invalid u8.
- Contract requires captures bool/u8 scalars and a shared reference to value; ensures takes
  `&MaybeUninit<u8>`, matching existing ensures macro syntax. Source metadata comes from real
  `proof`, `proof_for_contract`, `stub_verified`, `recursion`, and `unwind` attributes, following
  simple_replace_pass.rs, gcd_rec_simple_pass.rs and gcd_replacement_pass.rs examples.
- Depth is u8 selected from {0,1}; body takes subtraction only for depth>0. Source recursive edge
  strictly decreases it. Both companions preserve source contract semantics; the SimpleCheck
  companion explicitly expands the one step and has no recursive attribute/self-call.
- Generated Replace calls any_modifies before ensures assumption (`replace.rs`); generated
  RecursiveCheck uses bool REENTRY and check/replace closure dispatch (`bootstrap.rs`). Actual
  transformed-mode/body/transfer binding remains pending, not inferred from these source APIs.
- Standalone CLI accepts no `--edition` option in this base; runner uses default edition, whose
  syntax suffices here. `--exact --harness`, keep-temps, export-json, unstable-options and
  harness-timeout are existing driver options; the consuming cbmc-args is last. No gen-c,
  custom solver, no-assert, slicing change, skip or hook override was added.
- JSON fields follow `kani-driver/src/frontend/schema_utils.rs` and existing export tests:
  run/harness outcome.kind, outcome.verdict, attributes.kind/verified_stubs/unwind_value,
  contract.recursion_tracker, resolved_unwind, summary, failed_properties, checks and covers.
  Unsupported array contains successful properties too; only non-SUCCESS/UNREACHABLE entries
  become gaps. Successful unsupported guards are not falsely classified as failures.
- Consumer requires all failure IDs/counts and complete check/cover partitions to agree, and
  rejects unknown/error/undetermined statuses. It stores the untouched full export and full
  failure objects. Schema version is checked; shared schema and validator are unchanged.
- Popen uses a fresh process session, wait cap and process-group kill/reap on outer timeout.
  No export/stale output/incomplete outcome yields an explicit collection error and downstream
  NOT_RUN. Synthetic tests mock invocation; they do not run Rust, Kani or CBMC.

No Rust operand coercion, new unsafe compiler operation, trusted rule or production diagnostic
error path is introduced by these docs/test-only changes.
