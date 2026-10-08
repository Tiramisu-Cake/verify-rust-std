# Stack-address admission and ownership controls

`stack-address-cases.rs` now includes an isolated `stack_address_parameter`
frontend rejection. The fixture has one source parameter, so the Rust MIR
convention gives `_0` as return place and `_1` as that parameter. The marker
uses positive literal `1`; the translator rejects it at the return/parameter
guard before testing struct materialization. The expected location follows the
already calibrated marker-name span, and the exact error is
`mir_stack_addr(1): return place and parameters are forbidden`. The hosted
runner must still confirm the intended frontend stage and zero body entries.
The zero-ID fixture checks the syntax domain: `mir_stack_addr(0)` cannot reach
the return-place branch because only positive IDs are admitted. This is not a
claim that a return-place address was separately tested.

Hidden scalar and source-named struct rejections cannot use an ID copied from
the actual merge or an older fixture. For each, first make an independently
extracted fixture whose ghost line already contains one syntactically valid
marker call with a provisional high ID. Capture normal-preprocess MIR with
the exact Verifast exporter arguments on the hosted runner. Decode it and
identify a single candidate by its actual declaration index and role:

- For a hidden scalar, require a nonparameter, nonreturn raw local whose type
  translates to a scalar and has no VDI/source alias. Link it to a unique
  runtime assignment/source span; a guessed numeric ID is insufficient.
- For a named Range or tuple, require the raw struct local to have the VDI
  source name being tested, and link its declaration to the runtime source
  construct. Reject if the compiler instead creates a hidden temporary for
  that expression and the chosen ID is not the named local.

Replace only the provisional literal, export/decode the **final** source again,
and require the candidate's ID, type, role, VDI status and source span to be
unchanged in that final MIR. The final ghost marker and source hash must match
the checked source. Calibrate the exact translator error, target location,
frontend rejection class and zero body-entry count from that hosted run before
promoting either fixture to an accepted control. No local exporter/verifier
run and no unchecked hard-coded scalar/source ID is permitted.

Permission controls belong to the actual accepted hidden-struct proof, not
the frontend syntax suite. With the same source version, tool profile and
complete normal/unwind posts, separately omit one existing Range field/padding
chunk or tuple field/padding chunk from the loop invariant and require failure
at the specific invariant/resource or leak obligation. A forged points-to or
`T.own` must fail at its own production/consumption obligation. Retain the
full frame, iterator, `F` ownership and callback-unwind gates in the positive
baseline. An AST-linkage rejection for a wrong address is an admission control,
not evidence that a permission-negative reached its intended proof obligation.

## Hosted two-pass preparer candidate

`stack-address-control-templates.rs` has three separate CASE blocks with two
ghost marker occurrences each and a provisional `999999` ID. The named Range
and named tuple are forced into runtime MIR by `core::mem::forget`; the scalar
control uses the unique hidden `usize` result of `n + 1` passed to
`core::hint::black_box`. These are diagnostic functions only; they do not
change the actual SmallSort source. No ID from a previous compiler artifact
is included in their final form.

`stack-address-controls-prepare.py` is restricted to an owned GitHub-hosted
Linux run. For each CASE it extracts exactly the same prefix/body bytes as the
proof runner, executes the normal-preprocess exporter with
`verified/lib.rs --sysroot=... --edition 2021`, decodes with the pinned schema,
and imports the existing full-consumption `CapnpText` parser from
`stack-address-admission.py`. The initial pass demands one source VDI local of
the exact Range or three-`usize` tuple type, or one hidden `usize` destination
of the source `n + 1` binary Add. Every candidate must be a unique declaration
after the return place and parameter. It replaces the placeholder in both
ghost calls and the expected-error comment, reruns normal export/decode on
the final source, and demands identical ID, type, VDI role, declaration span
and source location. Finally it checks that the combined prepared fixture's
CASE extraction reproduces every final-exported source byte for byte.

The preparer has per-stage and total hosted deadlines capped at 20 and 60
seconds. It records binary/decoded/source hashes and refuses to reuse an
output directory. Its `ROLE_STABLE_NOT_YET_VERIFIED` certificate only makes
the fixture ready for the ordinary hosted runner. Frontend rejection is not
accepted until that runner gets the exact expected message/target span,
unchanged source, successful exporter/decode/refinement, and zero body entry.
If scalar lowering is `checkedBinaryOp`, source VDI is absent, or any role
drifts after replacement, preparation fails as setup; no expected negative is
claimed. The existing positive actual 14-address AST/resource gate is separate.
