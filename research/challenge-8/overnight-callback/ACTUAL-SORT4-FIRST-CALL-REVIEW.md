# Actual sort4 first callback: O19 cut and next admission boundary

O19 run `37746579002` proves the isolated `callback_positive` function with
full current two-cell, comparator, thread, normal and unwind posts and leak
checks. It does **not** prove `sort4_stable`. This note uses the O19
`actual-sort4-borrow-prefix/fixture` source and both complete decoded MIR
artifacts as a static design input. The std source is
`library/core/src/slice/sort/shared/smallsort.rs` at pinned std
`cd371e035c7e573760c43bf934d53e8118ee3e7d`; the worktree file SHA-256
is `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
No sort4 recovery hook is proposed for activation from this evidence.

The first unchanged Rust call is
`is_less(&*v_base.add(1), &*v_base)` at std line 620 (verified fixture
line 109). Its NORMAL typed MIR block 22 builds the ordered tuple from
shared-ref temporaries `_28` and `_32` into `_27`, then calls
`std::ops::FnMut::call_mut<F, (&T, &T)>` with `Move(_26), Move(_27)`, writing
`_25`, normal target 23, `unwindAction=Continue`, `isCleanup=false`.
Readonly MIR assigns different block numbers but retains the same typed call,
source span, ordered tuple, direct Continue action and non-cleanup call block.
This is one particular call cut, not a certificate for all five comparator
calls or their intervening pointer computations. Both O19 decoded whole-body
graphs contain exactly five `FnMut::call_mut` calls, eight
`hint::select_unpredictable` calls and four `ptr::copy_nonoverlapping` calls.
The counts alone do not establish their operands, edge graph or provenance.

The O19 prefix split four initialized input cells and their four `T.own`
chunks. It borrowed/share-packaged cells 1 and 0 into the two stock
`FnMut::Args` references. Its full verifier reaches the actual call and
then fails the unchanged unwind post at `array<T>(v_base, 4, _)` on verified
line 73; the array was split and the two borrowed cells were not recovered.
The destination array has not been written at this first call. The needed
checked route is: close the two reference debts; exit the exact lifetime
binding; call an ordinary verified `recover_pair` for cells 1 and 0; keep
current cells 2 and 3, destination, `F.own` and thread framed; then invoke
an ordinary checked `join_four_owned_cells` to close `foreach` and `array`
from all four *current* owned cells. This join must occur on the unwind
edge before consuming the original full unwind post. On normal return, the
two borrowed cells must likewise be recovered before the next comparator;
rejoining all four is one simple invariant for the next call's preparation.
No old `source_before` values or comparator rollback may be substituted.

The existing callback frontend patch only admits two named diagnostic
functions with `left`/`right` parameters and one direct Continue call. It
does not admit `sort4_stable`. The prefix fixture's `let_lft 'cmp = cmp_k`
is bound to the entire real `unsafe` block, so its reserved half lifetime
token cannot be assumed available between `c1` and `c2`. The separate strict
lifetime-cut draft owns this scope question and has its own kernel/trust
review; this note does not request changing it. Any generalized callback
adapter must be reviewed as new trusted semantics before implementation.

Before even a first-call diagnostic, require a fail-closed exact source and
complete typed-MIR certificate for the pinned body/contract, unique marker
and first call span, ordered operand def-use chains to `v_base+1` and
`v_base`, exact F/T/tuple substitutions, normal successor, direct Continue
unwind, absence of an intervening real cleanup or Drop, and AST placement of
debt close, scope exit, checked pair recovery and join-four before the
original unwind return. Check NORMAL and readonly MIR independently; block
indices are not stable between them. Source mutations (swapped/duplicated
argument, moved/duplicate marker, wrong function/call) and typed-MIR
mutations (operand, substitution, call count, successor, cleanup/Drop)
must reject at admission. Separate proof negatives must remove one fraction,
close token, borrow-end token, half lifetime token or one framed cell/owner,
and must fail at that resource obligation after valid setup. Ordinary panic
and shared-cleanup cases must retain their original actions. A green first
call would still leave the other four calls, pointer selections, copies,
generic/ZST domain, destination initialization, stability and composition
open.

## Candidate default-off integration profile, before code

The first-call overlay should be a distinct opt-in component, disabled in
ordinary verification and all existing callback fixtures. Its source marker
must identify the exact call and carry explicit source-written ghost debt
closure, checked pair recovery and checked four-cell join; the translator
must neither synthesize owner predicates nor retag the result. The existing
HRTB component already requires a named target and exact per-call compiler
projection match; `sort4_stable` may be added to that target list only after
the same whole-body certificate passes. The existing tuple-own predicate and
stock `FnMut` contract remain untouched.

The strict-lifetime draft's source API is
`//@ end_lft_binding::<'cmp>();` immediately after `c1`, inside the same
real `unsafe` brace as the unique `/*@ let_lft 'cmp = cmp_k; @*/`. It
relocates the original exported ghost block end from that brace to the
marker, retaining the old brace as one verified no-op and preserving the
rest of the real unsafe body's control flow. The marker itself is not
executed on `c1` unwind. The synthetic direct-unwind path must close the
two debts while still inside the lifetime scope, exit that scope through its
checked continuation exactly once, then run `recover_pair` and
`join_four_owned_cells`, and finally use the original unwinding return. The
normal path must exit through the same checked scope rule before its own
recovery and continue to the unchanged `c2`. A strict exit rejection for a
live `'cmp` chunk or escaped F bound is a real proof failure, never grounds
to remove the check. The lifetime patch owner has confirmed this proposed
API and ordering but is still auditing snapshot and escape correctness;
neither the draft cut nor its callback composition has a hosted result.
This note supplies no kernel change.

The source/MIR gate should pin the entire original std file and a byte-exact
ghost-stripped `sort4_stable` body, not only a call substring. It should
enumerate all five comparator, eight select and four copy call sites and
their typed arguments, destinations, normal/unwind successors and cleanup
bits in *both* modes. It should tie the one selected first-call operands
through their shared-ref/offset def-use chains to distinct source cells 1
and 0, prove each selected pointer stays in the same four-cell allocation,
and pin all ghost annotation spans relative to the real call and lifetime
scope. The full graph must have no additional Drop or cleanup operation
crossed by the injected continuation. If the compiler exports a Cleanup
successor or an extra runtime operation, admission rejects before proof;
no ad hoc cleanup bypass is permitted. The runner must record the effective
patch chain, opt-ins, source and complete MIR hashes and an AST/proof trace
showing exactly one transformed direct-unwind edge and unchanged unmarked
edges.

This first-call profile is deliberately diagnostic. It retains the entire
unchanged runtime body, so verification may fail naturally at `c2` or a
later operation after demonstrating both first-call continuations. Its
diagnostic normal post retains optional `dst` and cannot claim the target
initialized destination; its unwind post remains the full current four-cell
input array, optional destination, current F owner, thread and type
interpretations. A subsequent whole-function profile must restore the full
initialized-destination normal contract and cover `c2` to `c5`, the eight
selections and four writes before any sort4 proof claim.

`prepare-actual-sort4-first-call.py` is a hosted-only source-preparation
candidate. It reuses the already source-pinned O19 borrow prefix and the
checked `comparison_debt`/`recover_pair` definitions, adds an ordinary
`join_four_owned_cells` lemma that closes the exact four current cells into
`array` and `foreach`, and inserts only ghost comments around the first
unchanged Rust call. Its output deliberately says `CALIBRATION_ONLY` and
cannot enable any semantic component. The marker
`__vf_sort4_first_unwind()` is reserved for a future separately reviewed
frontend patch; with the current frontend it is not admitted. The source
builder itself has not been executed or hosted, and the join lemma has not
been verified. Calibration must first capture and review new paired complete
typed MIR, provenance/alias chains and AST scope shape. Nothing in the
builder's intended inventory is an admission certificate.

The builder's optional `--capture` route is hosted-only and runs only paired
NORMAL/readonly MIR export/decode, complete graph inventory and refinement.
It clears semantic opt-ins, does not invoke full VeriFast, and reports
`CALIBRATION_PAIRED_MIR_REVIEW_REQUIRED` only when those support stages and
source-integrity checks pass. A captured graph is still unreviewed until the
separate admission gate and human full-graph review agree.

The join-four lemma's array closure requires `pointer_within_limits` at all
five boundaries, including the one-past-end `base+4`. Its body now calls
the stock `points_to_limits` lemma on each of the four already-held
initialized cells and checks those five pure bounds before closing the
recursive `array`. This derives the bounds from existing cell permissions;
it does not assume a new source-array fact. The arithmetic link from the
fourth cell's object limit to `base+4` is a falsifiable hosted proof
obligation. If it fails, retain the failure and review available source
array bounds before changing the lemma.

`run-join-four-controls.py` prepares an isolated positive and three
resource controls over arbitrary current `T` cell values, framed optional
destination, current `F.own`, type interpretations and thread. The positive
must verify the ordinary join lemma and caller post with return/leak checks.
The missing-owner variant removes only the third `T.own` from a valid
four-cell setup and must fail at the join precondition; the duplicate-owner
variant must fail at the extra first-owner caller post after a valid join;
the wrong-cell variant calls join at `base+1` and must fail at its missing
fifth-cell precondition. Each requires NORMAL/readonly export/decode,
ghost-strip identity, refinement and full verifier trace. A frontend/setup
failure or a negative that first fails in the lemma body is inconclusive.
This fixture adds no runtime std change and explicitly uses the existing
positive-size diagnostic domain. Generic ZST coverage remains open.

`admit-actual-sort4-first-call.py` is a separate hosted-only gate proposal.
It reads the prepared source pair and complete NORMAL/readonly decoded MIR,
rechecks whole-body source identity and each complete function record, and
structurally follows the first `FnMut::Args` tuple fields through both
shared-reference borrows to `v_base.add(1)` and `v_base`. It requires the
pointer-add argument to copy the original `v_base` input with constant
offset one and lead directly to the selected `FnMut` block. It inventories
all five/eight/four named operations, their direct Continue actions, and
absence of cleanup/Drop in both full graphs. Without a separately authored
reviewed manifest pinning both complete record hashes and source hashes,
its only classification is `CALIBRATION_REVIEW_REQUIRED`. Even with that
manifest it reports only `EXACT_FIRST_CALL_SOURCE_MIR_ADMITTED_FOR_REVIEW`,
never a proof or semantic acceptance. A hosted calibration must test the
parser's actual decoded shape before it can gate a semantic overlay.

## O21 join-four evidence and source-preparation correction

O21 run `37750512251`, proof commit `d2f657be`, verified the ordinary
`join_four_owned_cells` body and its framed caller with `0 errors found`
and both leak checks. NORMAL/readonly export/decode, exact source integrity
and refinement passed for all four controls. The missing-third-owner case
failed at the join precondition `own(T_typeid)(t,x2)` on line 8; the
extra-first-owner case failed only at its added caller post on line 61; the
shifted-base case failed at the absent fifth `points_to<T>` on line 9.
These are intended resource obligations after valid setup, not evidence for
the actual callback or sort4 body. They establish the join lemma locally
on this pinned profile and positive-size domain.

O21's separate actual-sort4 preparation stopped before MIR export with
`ValueError: first-call borrow preparation changed the actual call`.
The source-pinned O19 borrow prefix deliberately contains the unchanged
Rust call with an *inline ghost generic-argument annotation*. The builder
had searched that prefix for the ghost-stripped call bytes, so it found
zero matches. It now checks and inserts the marker beside the exact
annotated call bytes while still replacing only the original unannotated
call in the pinned std body. The final ghost-strip equality remains the
runtime-source guard. This is a source-builder correction only; it has no
hosted MIR or refinement result yet and changes no verifier component.

O22 run `37754201983` reached the next source integrity check and stopped
before sort4 MIR export with `ghost stripping failed to recover exact full
sort4 runtime body`. The inserted multiline first-unwind marker began with
eight spaces before `/*@`. The shared `strip_ghost` removes the comment and
its following newline but leaves those eight bytes, so the original eight
spaces before `let c1` became sixteen. The builder now starts this marker
at column zero; its content and the Rust call are unchanged, and the existing
whole-body byte equality remains mandatory. This correction still awaits a
fresh hosted source/MIR capture. O22's separate owner-preserving forget
adapter result has no bearing on the sort4 callback gate.
