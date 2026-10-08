# Actual SmallSort panic macro origin certificate

`panic-macro-admission.py` is a hosted-only read-only classification gate for
the actual `panic_on_ord_violation` function. Its body executes the repository
source `panic!("user-provided comparison function does not correctly implement
a total order")`. In the pinned nightly, the two lowered calls and the final
unwind return carry spans in the compiler sysroot's `core/src/panic.rs`, rather
than `verified/lib.rs`. A source-file-only body-execution classifier therefore
reports zero even though VeriFast's log shows the actual macro path.

The gate does **not** alter source, proof AST, VeriFast, contracts or the
classifier. It can produce an exclusively created JSON certificate only when
all its source, normal MIR, proof AST, provenance and log checks pass. The
runner may then count the three certified macro `Executing statement` records
for this helper only. Its other body, return, leak, dead-code, refinement and
actual-callee gates remain mandatory; a certificate cannot turn a failed
verifier result into success.

Inputs are `--normal-decoded`, `--normal-mir`, `--proof-ast`, `--source`,
`--provenance`, `--compiler-sysroot`, `--verifast-log` and `--output`. The normal
MIR capture must use the exporter's normal preprocessing with the same Rust
arguments as VeriFast. The strict Capnp and OCaml constructor parsers from the
existing stack-address gates consume both complete representations. The
certificate binds each input SHA-256, the owned GitHub branch, commit and run,
and the compiler panic.rs path and SHA-256. Without `--require-final` the output
status is only `CALIBRATION` and must never count as body evidence. Final
admission requires both `--require-final` and
`--expected-compiler-panic-sha256 <64-lowercase-hex>`, where the expected hash
is a separately reviewed, literal pin from the preceding hosted calibration;
the gate compares the actual sysroot file bytes with that pin. Supplying an
expected hash during calibration also compares it, but leaves status
`CALIBRATION`. The runner must not derive the expected value from the same
run's observed file. An already existing output is rejected before any write;
failure writes no certificate.

The repository `smallsort.rs` must retain SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
Git blob `40939f922bcb6fdc7ee0d30427fa861827043827`, and exact helper-body
SHA-256 `2732f3532a1d8796efc7d9b16221bdc1820d1a9e42a4e0de92d426a33a583e5f`.
Ghost stripping of the checked helper must reproduce that body byte for byte.
The unique checked macro invocation and literal must match the normal MIR
constant's source span.

The normal MIR must have one `panic_on_ord_violation` body, zero inputs, the
exact `req thread_token(?t)`, `ens false`, and
`on_unwind_ens thread_token(t)` annotations, and the two-block call chain
`Arguments::from_str` then `core::panicking::panic_fmt`. Both call terminators
must retain `Continue` unwind; the first normal edge leads to the second
block, and the second call has no normal target. Its argument is the first
result. Their source spans must be the pinned line/columns of the actual
`panic_2021` macro implementation in the **same** `nightly-2026-09-25`
compiler sysroot passed to the exporter. The gate reads those compiler source
bytes and records their hash; in final mode it requires equality to the
independently pinned expected hash. It rejects a missing file, wrong source
path or version, and a line that no longer contains the `panic_fmt` and
`const_format_args!` macro call. Calibration's observed source-byte hash is
not by itself an admission pin or a semantic axiom.

The unique implementation `Func` in the proof AST must retain the full
`returning -> false` and `unwinding -> thread_token(t)` post, the exact string
literal's checked-source span, the corresponding `from_str` switch's normal
assignment and unwind return, `panic_fmt($_3)`, and its explicit unwind
return. The verifier log section between this helper's `Verifying function`
header and the next function header must contain the exact ordered two macro
calls, their execution records and one unwind return, followed by cleanup
and a checked-source leak check. Function-scope local initializers cannot be
counted as runtime-body evidence. The certificate records three macro-body
execution events, two verified calls, one unwind return and one leak check.

The hosted gate runs thirteen in-memory rejection controls: wrong owner,
literal, unwind edge, macro span, duplicate owner, source hash, compiler
version, compiler path, compiler source hash, missing second call log,
missing unwind return log, initializers-only log and suppressed AST unwind
return. They are checks of
this classifier's fail-closed behavior, not evidence of proof soundness. The
current file is a candidate; it has not been executed locally, in accordance
with the repository's hosted-verification rule. A hosted admission failure
leaves the actual-callee body gate open and requires inspecting its artifact
before changing the acceptance rule.
