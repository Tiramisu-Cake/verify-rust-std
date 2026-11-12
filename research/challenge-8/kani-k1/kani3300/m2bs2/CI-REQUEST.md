# M2-B/S2 — one missing counterexample receipt, coordinator only

Status PREPARED/BLOCKER. No semantic candidate, no worker dispatch authorization, Cloud $0.
Keep source exact5f7 + unchanged M2-A ordinary-singleton.rs, C03 legal_ordinary_transfer,
default Assert, existing compiled toolchain and timeout300s / CBMC RSS>6GiB sampling watchdog.
No full Quick, heavy PFC, new runner/workflow or model diagnostic changes.

## Precise change to stage A

Reuse the same C03 cwd, source copy, compiler environment and complete recorded argv as R2.
Replace any --output-format=regular with --output-format=old, and pass CBMC --json-ui --trace
through --cbmc-args. One root and one solver. Example argument array, executable path chosen
from the coordinator's existing tool (the source flag comments do not configure the CLI):

```json
["kani", "ordinary-singleton.rs", "--crate-name", "m2a",
 "--harness", "legal_ordinary_transfer", "--exact", "--keep-temps",
 "-Z", "uninit-checks", "-Z", "function-contracts", "-Z", "unstable-options",
 "--output-format=old", "--cbmc-args", "--json-ui", "--trace"]
```

Preserve RUSTFLAGS `--edition 2021 -D warnings --emit=mir` and all other actual R2 compile/
solver settings, limits and source path layout. Do not use --only-codegen, concrete playback,
--compact-trace, --export-json, --sarif or --log-file. No property filter is needed for this
small unchanged singleton (R2 reported 3.052696s verification); this avoids changing the
property set. Old bypasses Kani's regular renderer (call_cbmc.rs:179–191), while explicit
--json-ui preserves CBMC result[].trace including hidden assignments without compacting.
Kani preamble can surround the CBMC JSON: isolate the JSON through the existing reporting
path, not by inventing a new trace framework. Do not infer a successful trace from exit1.
Old uses mock Kani status: require CBMC cProverStatus/result statuses and the actual process
exits available to the coordinator, not that mock's property count. If the existing runner
cannot expose a nested exit, report it UNKNOWN rather than substitute Kani exit.

## Return curated fields, not a full dump

First use an existing saved CBMC JSON trace from R2 if available; no repeat required then.
Otherwise the one diagnostic run above, with existing preflight only if required by transport.
Return source/tool/sysroot/CBMC binary and emitted GOTO hashes, complete actual argv/nonsecret
env/cwd/root/mode, original stage exits/signals, cProverStatus and every result status (including
extra/Unsupported/frame/reachability), raw resource units and actual watchdog enforcement.
Identify which supplied artifact/run belongs to which invocation. Hashes of local files alone
do not prove an exact5f7 compiler/source binding.

For failed full property ID
`<u8 as std::array::equality::SpecArrayEq<u8, 3>>::spec_eq.safety_check.1`, extract ordered
steps with original step/thread/frame/source coordinates and **both** operands:

1. Calling frame: inner Assert body equality, ensures predicate or root. Preserve the call
   chain through PartialEq and spec_eq; .1 is reused at all these sites.
2. raw_eq a/b and CheckAs pointers, runtime object identity + offset + extent3, emitted symbol
   or local instance; keep source AllocId separate. For ensures show captured out referent,
   for body show _16 returned from assume_init of _17, and RHS canonical AllocId symbol.
3. Every completed reset up to failure: nondet witness object/offset, initial false, all seed
   guards/results relevant to the selected witness. The emitted RHS seed already exists at
   GOTO instruction6941; report whether it actually fires, not another proposed seed.
4. In chronological order all assignments that change tracked_object_id, tracked_offset,
   value, selected transfer/buffer witness and snapshot fields; include copy_by_id,
   store_argument/load_argument, false/true setters and branch choices. Retain the last
   setter/retarget before the failed is_ptr_initialized result with enough neighboring steps
   to distinguish no setter from a later overwritten value. Include the _17 input false
   setter, assume_init normal return and _16/out instrumentation, if on the reached path.
5. Return original descriptor/Some-None/Freeze snapshots only if already available. Their
   absence stays explicit; no new instrumentation or source modification is requested.

If trace remains absent/truncated or hidden effects were omitted, report that exact limitation
and completeness boundary. A property name, last source location, literal bytes or reset GOTO
is not the missing runtime history. Do not fall back to raw archives/global logs.

## Acceptance after diagnosis remains HELD

No guessed registry patch, D0 setter patch, mutable seeding or ABI/DFCC/retarget redesign.
After a source-bound cause, use original M2-B/S narrow scope and per-expression type audit,
C03-form suite test and valid None/false controls, one Luna High review and build/fmt/clippy
before unchanged C03–C06 + required controls. m2bs/CI-REQUEST.md section B remains the control
list; original inputs/goldens are unchanged. M2-B/R resource gate is separate/unresolved;
full Quick and M3 remain HELD. This diagnostic request earns no semantic/B1/B2 proof credit.
