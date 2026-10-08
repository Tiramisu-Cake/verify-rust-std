# Callback direct-unwind recovery: design boundary

2026-10-08. Read-only design for the authorized overnight phase; no verifier
patch, fixture change, or hosted result is claimed here. Pinned source:
VeriFast `f76012fb518703b1d98e243ac4f487f16877cfcb`, std
`cd371e035c7e573760c43bf934d53e8118ee3e7d`, nightly 2026-09-25.

## Witnessed obligation

O13 run `37711416854`, artifact `overnight-s6/tuple2/callback`, executes the
checked `recover_pair` body and reaches the real `FnMut::call_mut` in the
unrestricted `T, F: FnMut(&T, &T) -> bool` positive. The first failure is the
callback's full unwind post at `*left |-> ?left_after`; the normal-path
`close comparison_debt` and `recover_pair` are skipped by direct unwind.
The stock FnMut unwind clause returns current `F.own`, storage and thread, but
consumes `Args.own`; the separate borrow debt is framed. No rollback of `T` or
`F` can be assumed. The target remains both current initialized T cells, one
current `T.own` each, current F storage/own and thread on normal **and** unwind.

The pinned translator emits `ReturnStmt(unwinding())` for MIR
`UnwindAction::Continue` (`vf_mir_translator.ml:2653-2671`) inside the call's
`SwitchStmt` (`:2690-2760`). Function-level `on_unwind_ens` parses a post; it
does not run ghost code on that edge. Source-positioned ghost statements after
the call belong to the normal successor. The verifier's block return
continuation frees locals and restores the reserved lifetime fraction, then
returns, bypassing trailing statements (`verifast.ml:2668-2681`). Existing
`TryFinally` AST support has no Rust ghost syntax/translation hook in this
frontend. An auto-lemma cannot call `close_frac_borrow`, `end_lifetime`, or
`borrow_end`: they require `nonghost_callers_only`, which auto-lemmas reject
(`verify_expr.ml:381-385`; `lifetime_logic.rsspec:76,122,280`).

## Narrow candidate for review before implementation

Attach a source-written, proof-only recovery annotation to exactly one
source/MIR-matched `FnMut::call_mut` with `Continue`. On the call's unwind arm,
execute **source-written** closure of the two already-open fractional
`ref_initialized` accesses into `comparison_debt`, then take a synthetic
proof-only `GotoStmt` to an outer label after the natural `let_lft` block.
The normal arm continues to the existing source-written debt closure and
ordinary recovery. The outer unwind label calls the **checked**
`recover_pair<T>(left,right)`, then performs the original
`ReturnStmt(unwinding())`. The goto must pass through the verifier's existing
block exit, restoring the reserved half lifetime token before `recover_pair`.
The debt predicate carries scoped reference identifiers and fractions, so
the outer continuation only names `left`, `right`, and the debt. The candidate
uses the existing `close_frac_borrow`, `end_lifetime`, `borrow_end`, and
`open_full_borrow_content` rules; it must not introduce a trusted recovery
lemma, an assumed owner, or a new kernel rule.

This is a **new trusted frontend correspondence**, despite being proof-only.
It needs a semantic patch/card and independent self-review before use. Keep
the annotation inert in ordinary Rust and prove byte-identical ghost stripping.
The exporter supplies ghost annotations to `translate_body`, which parses each
with `VfMirAnnotParser.parse_ghost_stmt` *before* translating MIR blocks
(`vf_mir_translator.ml:4903-4911`); a new syntax needs a deliberately narrow
parser form or a recognized existing parsed wrapper. Raw new syntax cannot be
intercepted only inside `translate_unwind_action`.
Fail closed unless one source marker maps to one decoded call of the exact
function/receiver/argument shape and `Continue` action. Reject duplicate,
missing, misplaced, mismatched or stale markers. Never rewrite `Cleanup`,
`Terminate`, `Unreachable`, other calls or normal target. For actual sort4,
each of its five comparisons needs its own independently audited resource
instance; later guard cleanup must execute in the original order.

## Acceptance gates for a hosted diagnostic

1. Positive: actual two-reference callback with unrestricted non-Copy T and
   unrestricted FnMut, full normal/unwind posts above, full body/return/leak/
   dead-code checks, unchanged stock FnMut spec and checked `recover_pair`.
   Inspect full proof trace for debt close on both branches and recovery before
   the unwind post. The post uses fresh *current* values.
2. Resource negatives: omit one initialization fraction, one close token,
   either borrow-end token or the reserved half lifetime token; each must fail
   at the matching debt close/recovery precondition, not setup or an unrelated
   helper. False current-cell/F unwind posts must fail at their exact posts.
   A false normal post must remain an intended separate negative.
3. Admission negatives: wrong call/arguments, wrong marker coordinate,
   duplicate marker, non-Continue action, or changed source body must reject
   before proof. An ordinary panicking call and a real shared-cleanup/Drop
   fixture must retain and execute their original unwind routes.
4. For every fixture: fresh NORMAL and readonly MIR export/decode; source,
   ghost-strip and call/edge/target audit; refinement; exact profile hashes;
   no disabled unwind, leak, dead-code, UB, validity or refinement check.
   A green diagnostic proves only the matched callback obligation, not actual
   `sort4_stable` or admissibility of the frontend patch.

Returning comparison debt as the callback unwind post can diagnose its frame,
but is deliberately partial: no full-target acceptance can use it. Extending
FnMut's unwind post to return `Args.own` is unsupported by the stock contract
and does not solve lifetime exit. Inserting recovery directly in the inner
unwind arm lacks the half lifetime token reserved by `let_lft`. Adding a runtime
`catch_unwind`/guard or restricting `T`/`F` would change the target.
