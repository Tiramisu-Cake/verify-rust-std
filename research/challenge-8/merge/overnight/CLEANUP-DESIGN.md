# Source-anchored callback cleanup — design before implementation

Status: DRAFT, not applied/accepted. Owner OVERNIGHT-MERGE-26.10 authorizes this
necessary model dependency; exact full actual callee goals remain unchanged.

The prepared opt-in profile and exact one-line annotation interface are in
[CLEANUP-PROFILE.md](CLEANUP-PROFILE.md). The source places `callback_close`,
`callback_scope_end`, and `callback_recover` on three consecutive ghost-only
lines after the real call and before `let src`. The middle marker supplies a
distinct exporter dummy: `find_blocks` can then recognize one lifetime-close
terminator without conflating it with the recovery commands. This is a draft
source/AST dependency until hosted compilation, proof and negative gates pass.

## Actual obligation and observed control flow

Pinned repository SmallSort source85c75bc9, merge_up677/merge_down710: FnMut call
may return either Boolean or panic after legal interior mutation. Full target
normal/unwind posts return current valid source cells and T.own plus current
F.own; normal performs one selected value copy and exact pointer advances,
unwind keeps destination/cursors untouched. Unrestricted T/F; distinct-source,
positive-size diagnostic domain is explicitly conditional. Coincident/ZST/full
scratch domains remain open, no Freeze/Copy/purity restrictions on this safety.

Pinned exporter evidence37705502655 resolves actual FnMut into an outcome switch
with UnwindAction::Continue. Rust panic becomes ReturnStmt(unwinding), not AST
Throw/econt. Stock BlockStmt restores held lifetime token halves on Return/Goto,
but does not execute source borrow_end recovery. Stock let_lft declaration spans
an actual Rust block; ghost-only braces cannot scope a runtime call. Historical
26.09 end_lft_binding patch is a design sketch, not an admitted dependency.

## Minimal opted-in mechanism

Use explicit ghost markers and two explicit source-provided ghost command lists:
inside-binding fraction closure and outside-binding physical loan recovery.
Validate a unique local let_lft and exact typed FnMut call with its real source
span and normal successor; admit Continue only initially. Marker cuts the local
binding before selected copy. Normal executes inner commands, leaves binding,
then outer commands. Panic executes the same inner commands and takes a synthetic
proof CFG Goto outside the binding, restoring its held token fraction there;
the epilogue executes outer commands and the original ReturnStmt(unwinding).
No normal memory/cursor command is moved onto panic. Unsupported cleanup actions,
multiple/ambiguous calls, wrong marker/type/span or reentered cut are rejected.

Ghost epilogues call existing checked/trusted RustBelt primitive contracts; no
axiom equates call completion with source ownership. They close each opened
ref_initialized_ fraction, end physical lifetime, consume both borrow_end tokens,
and open current full-borrow contents. Callback FnMut summary is the stock one.
A missing fraction/token/owner must fail at its own real resource obligation.

## Trust boundary and review

A separately hashed frontend CFG/scope dependency may reconstruct a strictly
checked local prefix and add ghost-only unwind epilogue. If a kernel strict-scope
mode is necessary, it must preserve EVERY linear heap chunk rather than using
stock lifetime-type filtering, restore outer lexical type/value environments,
and reject escaped binder-dependent types in locals, chunk types, projections,
predicate/function captures and bound metadata. Physical cmp_k-indexed resources
(lifetime_token, borrow_end_token and persistent shares) intentionally survive
until explicit end_lifetime/borrow_end; do not indiscriminately erase or reject
all physical k terms. Hidden type/capture inspection limitations must fail closed
or restrict the profile, never silently discard chunks. Rebase learned local
projection bounds on outer F to the entry snapshot without granting new equality
facts or ownership. Preserve kernel memory, validity, leak, unwind and dead checks.

Do not reuse stock TryFinally: its second verifier branch runs the resource-
consuming body with an empty heap (verifast.ml2272–2306). No generic Java/raw
exception semantics extension is justified by the actual Rust outcome route.
Exporter/decoder/refiner stay unchanged unless later evidence independently
requires a separately designed change. Verify generated proof AST/control flow
against original typed MIR; source stripping and source refinement stay exact.

## Required acceptance matrix

Positive: genuine source/F owner loans, both arbitrary Boolean outcomes, normal
current-value recovery before copy, panic after mutation returning current source
and F ownership with untouched destination, unrelated frame preserved; full
body/return/leak/dead/export/decode/refinement/source identity gates.
Negative: omitted left/right source own, comparator own, each ref-init fraction
closure/borrow-end token; live lifetime-typed local/chunk/captured predicate or
bound escapes cut; false unwind post; destination write on panic; unsupported
UnwindAction/multiple callbacks/wrong F/T/lifetime marker, CFG reentry/incorrect
cut. Exact stage/predicate/location calibrated before admitting a negative.
Regression: combined W1/M2/C1, full G2/A/B/oldRust/bridge, native and ordinary
normal/unwind/dead controls. No microfixture or component PASS is actual callee
acceptance until the unchanged complete callee body/full contract passes.
