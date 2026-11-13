# H1 STEP1: ensures closure layout blocks semantic qualification

2026-11-13; worker15. Read-only source analysis at production `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`
and upstream `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`, using local clone `/root/kani-fix-3300-h1-ci`.
CI overlay HEAD2657d2bc3a changes only workflows/ci/h1; production directories match4f64.
No repro, build, compiler, verifier, download or source/golden change was performed.

## Observed failure and its position

Every completed P1 (E8,D10,C12,F12,H16) has exactly one FAILURE:
`kani::internal::apply_closure::<std::mem::MaybeUninit<u8>, {closure@/home/runner/work/_temp/h1-input/scalar-pfc-legal.rs:14:17: 14:43}>.unsupported_construct.1`.
Description: cannot check initialization for pointers to that closure; `Cannot determine layout for an unsupported type …`.
P2(D10,C12) has the analogous hole-fixture Unsupported and two additional failures listed below.
CASES.json contains both complete316-property inventories, including all successful/unreachable properties, and exact source/hash references.
CBMC `properties.json` is incomplete (`object capture cap`, no retained properties); complete, hash-checked Kani regular output is the recovery source.
All completed P1 share305SUCCESS/10UNREACHABLE/1FAIL; P2 share303/10/3. No completed arm has a private frame/protocol failure.

Bounded, complete C12-P1/P2 GOTO projections independently place the closure CALL at line1741 (PC779),
Unsupported `ASSERT false` at1744 (PC780), then `ASSUME false` at1746 (PC781), before returning from apply_closure.
Thus this diagnostic follows the callback; it does not prevent the callback's payload checks from being reached.
It does prevent returning its bool to the enclosing contract assertion:
`postcondition_target::{closure#2}.assertion.1` is UNREACHABLE, not a passed useful postcondition.
The source location `library/kani/src/lib.rs:63:1` is a macro/instrumentation span, not the offending user payload read.
The complete C12-P2 symbol projection lines22848–22855 binds the exact ensures closure tag to `struct … { }`;
the source closure has no captures. This is a zero-sized environment, not a missing rustc layout query.

## Source route and concrete hypothesis

At4f64, `library/kani_macros/src/sysroot/contracts/shared.rs:143–157` wraps ensures in
`kani::internal::apply_closure(expr, &result)`; `library/kani_core/src/lib.rs:693–695` calls `f(x)`.
`check_uninit/ty_layout.rs:227–240,255–264,294–295,472–479` first obtains rustc layout, then computes data-byte masks.
Only `FieldsShape::Primitive` gets the zero-sized shortcut. Under `FieldsShape::Arbitrary`,
`RigidTy::Closure` explicitly returns `LayoutComputationError::UnsupportedType`; captured or empty closures have no supported mask branch.
The common `UninitInstrumenter` (`check_uninit/mod.rs:227–284`) converts this error into Unsupported;
the message says exactly which layout operation failed, unlike B1 call-resolution diagnostics.

The originating pass is consistent with global **DelayedUbPass / InstrumentationVisitor**, not a failure to resolve Fn::call:
`delayed_ub/instrumentation_visitor.rs:122–198` emits CheckRef for target reads and SetRef after mutations
whose ancestor sets overlap targets. It operates on ordinary places/references as well as raw-pointer accesses.
The local raw-pointer visitor only emits its generic dereference checks for raw pointers (`ptr_uninit/uninit_visitor.rs:791–802`);
the `f(x)` receiver is a reference to the closure, and a closure is not one of that visitor's ADT/Dynamic drop setters (734–755).

Concrete hypothesis: S3 restores points-to propagation through the emitted registration trampoline; the field/context-insensitive
closure-call graph overapproximates the empty receiver as related to the returned MaybeUninit payload.
In `points_to/points_to_analysis.rs:478–501`, tuple-argument aliases are added to **all** callee parameters, including local1 (closure receiver).
The closure environment consequently acquires a target/common-ancestor relation; a normal-return mutation/drop setter on `f`
then requests the unsupported closure mask. Its after-callback position matches the saved GOTO.
The exact source MIR operation, alias seed and needs_get/needs_set decision are not in these receipts:
the setter/drop attribution is a specific source-based hypothesis, not a traced converter/visitor fact.

S3 (`delayed_ub/mod.rs:93–139`, body-overrides path) is the plausible **exposure** change: it follows actual registration bodies
instead of their source panic and keeps discarded closures unreachable. Reverting it would lose required normal-return tracking.
B1 `resolve_call` (`points_to_analysis.rs:355–385`) accepts resolvable MIR-backed Item/Shim and emits distinct call-related reasons;
it has no closure-mask computation. The observed reason is not evidence that B1 rejected a call.

## Upstream comparison and previous visibility

Upstream bf9c58e662 already has the same explicit `RigidTy::Closure => UnsupportedType` at ty_layout.rs:393–400,
the same closure-parameter alias overapproximation at points_to_analysis.rs:478–501, and the same generic delayed-UB place setters/checks.
Therefore the layout limitation and failure route predate Part1; a tracked closure can encounter it without Part1.
This is a code-level conclusion, not an executed upstream P1 result. On exact upstream PFC, delayed analysis follows source
registration bodies (`delayed_ub/mod.rs:106–108`, no S3 overrides); Part1's MU transfer support is also absent.
It is unjustified to assert that the identical P1 reaches the same property, or passes, on that upstream revision.
Upstream's old unsupported_call accepts resolved nonvirtual FnDef calls; B1 did not introduce the blanket closure-layout rejection.

At b16, A16 is stopped by an RSS watchdog before any first-CNF count/verdict, hiding this property among unresolved obligations.
Prior resource-limited runs could not establish its absence. Restricted Quick retained clause/frame cases and excluded legal-pair/postcondition-hole
(the recorded S3 Quick scope); those controls have different bodies/paths and do not qualify this useful ensures read.
Source/test selection and OOM history explain a coverage gap, not evidence that no earlier tool revision could produce this diagnostic.

## Why P2 reports two uninit checks

Both D10/C12 P2 fail `std::ptr::read::<u8>.safety_check.1` and `.safety_check.4`, at core/src/ptr/mod.rs:1754:9.
The first description names `*const u8`, the second `u8`. Both test **pointee initialization**; the first is not a failure
of the pointer value's own initialization. Labels come from the instrumented operand type (`check_uninit/mod.rs:431–451`).
The saved C12-P2 projection binds ensures callback → MaybeUninit::assume_init_read (4462) → pointer.read (6281) → ptr::read (6258).
Inside ptr::read, PC1822/line3979 calls `is_ptr_initialized::<1,u8>(src,[1])`; PC1823/3982 is the first check.
PC1828–1829/3993–3995 forms another pointer `&*src`; PC1832/4001 performs the same one-byte initialization query;
PC1833/4004 is the second check, followed by ASSUME at4006 and the sole payload assignment at4009.
This matches local raw-pointer `Check` plus global delayed-UB `CheckRef`, not two source payload reads or two separate holes.
The first generated assertion has no following assume; the second does, so both may be reported for the same bad payload.

P2 **does not satisfy** the literal R3 oracle “exactly one failed property”: there are three, including an unrelated Unsupported.
Removing the Unsupported alone would still leave two properties. The paired uninit failures are consistent with the intended read,
but do not justify silently deduplicating the oracle or awarding semantic credit. Any future oracle clarification must explicitly retain both obligations.
Source/projection call binding is stronger than a count/label, but a full counterexample/path/points-to audit remains unavailable.

## Minimal repair path — proposed only

For this exact empty closure, support an explicitly **sized, zero-byte** closure in data_bytes_for_ty with an empty mask,
before the Arbitrary-fields unsupported fallback. Preserve nonzero closure rejection, all safety/frame/protocol checks and S3 propagation.
This is a representation repair for a type with no data bytes; it must not turn unrecognized/nonzero/unsized types into empty masks.
A broader closure implementation would recurse over monomorphized capture types using rustc field offsets, preserving padding and union limitations;
it is a separate scope, not necessary for the first distinguishing repro.
Before acceptance: check empty closure after successful/failed callback, a captured initialized scalar, an uninitialized capture/alias negative,
then exact P1/P2 and frame/clause controls at matched resource settings. P1 must reach/pass the outer useful assertion;
P2 must retain both actual uninit obligations pending explicit oracle policy. No check suppression, assumes, S3 rollback or golden weakening.
An alias-precision repair should be considered only with exact MIR/points-to evidence; blindly skipping all closures risks dropping captured data.
No fix was implemented; general symbol/assigns/reached-write binding, supported profile capacity and proof credit remain UNKNOWN/zero.
