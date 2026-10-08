# O17 H2b audit and classifier amendment rationale

Hosted O17 source `11d888ba8ff2231a80c759148194aa9ae6b9d30e`, run
`37717092130`, used H2b patch SHA-256
`c9afb4bfd696efc38f2bc71e10463a34170d9d769e851a07388c01278e99b2ff`.
The source of this review is the complete downloaded H2b/generic-method
case summaries, fixtures, NORMAL and readonly MIR, full verifier logs and
refinement artifacts under `/tmp/overnight-o17-evidence/overnight-s6`.
These artifacts are not committed. O17 classifications remain historical;
the classifier amendment below applies only to a future hosted run.

The H2b `positive` local unit exported and decoded in both modes, refined,
passed exact H2a source/MIR gate, and verified with exit 0 (`0 errors found`,
71 statements). The checked generic pointer-drop method has normal and
unwind return/leak checks. The nominal constructor closes an owner from a
real initialized `*slot` and `T.own`; the concrete `u32` witness closes
ordinary scalar owner from an existing cell and calls that constructor.
The local source-shaped `DropOnPanic<T>::drop` opens its generated full
borrow and truthful owner, calls that checked method, then passes normal and
unwind return/leak checks. `OrdinaryDrop::drop` is verified in the same unit,
showing the selected template does not alter that ordinary Drop case. The
actual std nested Drop DefPath has **not** been verified or linked in this
profile, so this is a local H2b component result only.

Four source-admission mutations (`method_operand`, `guard_operand`,
`owner_predicate`, `field_visibility`) each pass paired export/decode and
refinement but reject at the expected exact-source gate with verifier exit 2
before the local method is entered. `missing_cell` and `wrong_target` each
fail at the owner close's `points_to<T>` requirement at verified line 28;
`duplicate_owner_post` fails at its extra `*slot` post at verified line 37
after the constructor return. Those are intended resource obligations, not
setup failures. All retain their original O17 labels.

The separate six-case generic callee matrix has full verifier exit 0 and
normal/unwind return/leak for its positive method+probe. Missing owner fails
at the callee pre, false normal and false unwind fail at their exact false
posts, and retained `T.own` fails at the caller normal post. The
`retains_initialized` case has verifier exit 1 after the checked callee and
probe normal return. Its sole error is at
`prelude_core.rsspec:213`: auto-closing `points_to<T>` for the probe's
`ens *slot |-> value` requires `some(value)`, but the actual returned cell is
`dummy`/optional. The log explicitly points back to the probe's verified
line 25 consuming assertion. The original classifier required the first
error to be in `verified/lib.rs` with `No matching heap chunks` and therefore
correctly labeled O17 `DIAGNOSTIC_ONLY`. This is nevertheless the intended
optional-versus-initialized post entailment, expressed through the stock
predicate definition. A narrow future classifier may recognize exactly this
prelude error **only** when there is one error, source/refinement/paired-MIR
stages pass, both generic method outcome paths return/leak, the probe was
entered, and the log has the exact verified normal-post consuming assertion.
No verification semantics, contract or fixture is changed.

Outstanding before H2b ACCEPTED: direct actual nested std Drop linkage and
source/MIR certificate; resource controls for its caller/cleanup paths;
review of the generated selected template on actual ADT versus local copy.
The generic callee's `retains_initialized` improved classifier alone cannot
promote H2b or the actual helper. O17 contains no accepted actual nested
Drop proof.
