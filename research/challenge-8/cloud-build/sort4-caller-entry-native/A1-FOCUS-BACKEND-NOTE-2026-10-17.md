# A1 focused stage collector (UNRUN)

`a1-focus-backend.py` is an import-inert Cloud-only collector. The pinned
VeriFast console accepts `-focus verified/lib.rs:<line>`; `check_focus` uses
the function's source span to select symbolic execution. The collector first
locates the certified source declaration, then performs the full paired
normal/readonly export, decode and refinement. It derives the actual focus
line from the compiler `Body.span.lo` for the numeric threshold item or
observer. It checks `fnSigSpan.lo` against the threshold declaration but
never uses that signature line as a proxy for the AST body focus. The
interface-only stage uses line `0`.
It uses the exact A1 phase, profile, proof/infra SHAs, final tool receipt,
source certificate and verified/original byte pair. The compiler sysroot may
reside outside `/workspace`: the frozen lane derives it from `rustc --print
sysroot`, so the collector checks its directory, active sysroot, rustc commit,
toolchain and host target instead. Mutable working paths remain under
`/workspace`. Final verifier/exporter/schema/source hashes are checked both
before and after the focused stages.

For each isolated case it calls `selected-runtime.source_support` first. That
path exports and decodes the full normal and readonly source unit, captures a
unique observer MIR record, and runs refinement over the complete paired
unit. Only after paired support succeeds does it run one focused verifier
invocation with `-dump_ast_with_locs`; the AST is emitted by the frontend
callback before the proof verdict. A nonzero exit can therefore be the intended
negative while still yielding an AST. The dump target is a fresh absolute
path inside that case's evidence directory; a preexisting dump at either
the fixture or target path is rejected before verification. A missing AST is
inconclusive. No
exporter or translator body filter is used. The focused
CLI contains no assume, ignore, or disabled-unwind switch. The same shared
Build deadline caps every stage.

The output is `a1-focus-raw-observation.json`: exact focus argument, stage
commands/exits, artifact paths and hashes, source pair pins, the paired
support report, and the numeric compiler item selected from the paired MIR
inventory when available. It deliberately leaves body count, native post AST
equality, and proof verdict unclassified. In particular,
`-focus` selecting a line does not itself prove which numeric compiler item
was checked or establish native conformance. An independent same-Build
compiler/AST classifier must inspect those facts before creating any
`A1Admission` record. Caller stage also requires the prior two-body receipt
to exist, but this collector never writes or publishes a receipt. The
`N-false31` verified source bytes differ from the positive baseline; its
receipt must bind that exact verified/original pair. The outer runner must
re-prove both threshold bodies and conformance for that pair, or use only a
reviewed proof cache keyed to the identical byte pair. A positive-baseline
receipt cannot be reused for the false-31 caller stage.

No Cloud run, local compiler, exporter, verifier, or proof was executed.
The exact stage behavior and focus-to-item mapping remain UNRUN Cloud gates.
