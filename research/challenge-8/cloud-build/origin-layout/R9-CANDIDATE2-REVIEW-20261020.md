# R9 candidate 2 independent review — GO for code and controls

Reviewed tool commit `899c9d7e4ef8370e53926ee6813baa97bb71d701` against its
parent tool `ec985deab9c58bd485c17e9542acee83062986e9`, and the source runner
changes against project source `1744fe3911b824f8ecd6f34f455b89c2ca1d0fc9`.
The review covered the native translator and diagnostic changes, `first-callback.py`,
`r9-guard-return-controls.py`, and the R9 marker/controls/phase/wiring service
tests. This is a static code and synthetic-service review; no local preparation,
compiler, formal proof, or Cloud Build was run by this reviewer.

The recovery marker is R9-only and source-bound. It must be unique and occur in
the admitted first+late callback body with the unit's exact selected generated
Drop key/path/hash/guard. The hook records the original MIR block, normal target,
cleanup bit, and selected local, requires the same local across matching edges,
and rejects duplicate execution or a missing returning-edge translation. It
removes the marker block from ordinary source ghost statements and inserts the
source-supplied commands in a fresh `PureStmt(BlockStmt)` only after receiver
`finish` on the selected Drop `returning` arm. The own-unwinding arm is unchanged.
The source commands still pass through ordinary kernel checks; no predicate,
assumption, permission premise, or resource is synthesized by the translator.

The runner copies and sanitizes case environments, enables recovery and tracing
only for the nonprefix R9 actual callback case, and leaves the parent environment
unchanged. Other profiles and prefix cases strip stale R9 flags. The kernel
trace only formats the current heap/environment (at most 48 chunk rows) on the
opt-in path and continues with the identical heap and environment. The tool-side
change is diagnostic and CFG-local; R8 allocation behavior and default-off
behavior remain unchanged when the recovery marker/environment is absent.

The controls runner fails closed on source/profile setup errors, missing or
partial stage/source receipts, setup exits, null or wrong-type execution
receipts, wrong diagnostics/locations, and event-binding mismatches. Baseline
and mutant stage receipts bind both exact source hashes at every stage. Mutant
MIR position may change, but the event must have nonempty own-case MIR identity
and match the baseline caller and selected Drop identity. Resource refusals
require the exact target to have executed last before one verifier error, the
expected predicate/spec signal, the bound cleanup returning event, and no
recovery-complete event. Admission controls bind the marker's actual frontend
error to the enclosing function/block source line. All classifications retain
`accepted=false` and `proof_credit=false`.

Synthetic verification passed: nine guard-return control service tests, marker
placement/environment checks, six phase authorization tests, and the R9 wiring
test. The phase test permits the live budget to evolve while preserving the
fixed phase identity and checks that used plus remaining seconds equals the
ceiling. No coordinator implementation was changed. The tracked `src/verifast.ml`
is CRLF; its commit diff passes with `core.whitespace=cr-at-eol`.

**GO for the reviewed code and controls.** This review grants no proof credit and
does not accept the experimental profile. Refreshing the profile digest and
pinned project inputs is a separate closure step before any proof submission.

Main integration note: late-admission mutants copy full R9 source, therefore
their explicit R9-only dispatch restores marker environment; independent Luna
review GO for this localized lambda. Prefix admission controls remain skipped
when prefix fails. Its additional internal fullbody-cleanup replay uses its own
runner/env; if prefix later passes under R9, review its environment selection
before claiming that subgroup qualified. No current skipped subgroup credited.

Final closure: tool899c9d7e4ef8370e53926ee6813baa97bb71d701, profile
8685a04dfdc2afba86994580ec55cf872da09b311534ff2d1fea22f35debc1a7.
Static19patch/17sourcepins/18retainedbase PASS; exact inputs include recipe and
newmarker/control service modules. Source model/prelude/options and R8 allocation
patch unchanged. All source/actual claims remain pending Cloud, qualificationOPEN.
