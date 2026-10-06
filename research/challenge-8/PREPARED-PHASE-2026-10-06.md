# Prepared phase feasibility review, 2026-10-06

Historical closeout: the later owner decision selected the bounded
[sort4 phase](SORT4-PHASE.md). This insertion/ManuallyDrop phase remains closed.
Use [STATUS.md](STATUS.md) for current authorization.

Owner explicitly resumed the bounded phase from STATUS after instructions commit
f50b237. This report concerns feasibility; it is not a whole insert_tail proof
or authorization for any new architecture/tool semantics. No local compilation,
verification, extractor or executable test was used.

## Draft review and resource route

The saved DRAFT-MD-RECOVERY-2026-10-06.patch remains unapplied. Its split_fraction
statement multiplies the current chunk by first_fraction; it does not restore an
absolute first_fraction from the merged first_fraction+second_fraction chunk.
A ratio would require positive/strict coefficient conditions not supplied in the
open_frac_borrow contract. The opaque ref_initialized predicate must not be used
to invent bounds or assume an equality bridge.

The revised fixture instead keeps each exact initialization fraction and its
matching quarter-lifetime close token in an imprecise single_initialization_access.
The caller packages the first access before opening the second. The genuine
shared-reference creation uses the second access. recover_single unpacks/closes
the first completely before unpacking the second. The two original quarter
lifetime accesses and full current storage/T.own post remain unchanged. There
is no coefficient restriction, split, assumption or verifier change. Baseline
controls exclude the optional helper even in the minimal patched profile.

Hosted diagnostic: run37448257248, source
f0f417ce9913f53a90591c89593b31b359b87032, selection
verifast_borrow_recovery_manually_drop,90min. Completed/failure: actual helper body16records through return/leak-check;
five baseline controls pass; both MD callers fail before actual reference/helper
call at full borrow construction. Original RawPtr refinement failure is retained;
this diagnostic is not the accepted lifecycle gate. Separate unchanged-release
run37448682524 on the same SHA passes all five baseline controls.

## First caller blocker: immutable local storage

Both MD callers now reach close_full_borrow_content<T>(t,&tmp), generated source
line95; both fail general.rsspec:203 with missing points_to<T>(tmp_addr,_).
Pinned translator:1880-1892 maps immutable MIR local Not to ConstTypeExpr.
Verifier verifast.ml:991-993,1042-1044,1111-1118 creates half storage permission
for addressable const locals. In contrast general.rsspec:202-204 requires full
points_to plus T.own. This is a half/full permission mismatch, not evidence that
ManuallyDrop::new discarded the value. The actual source also declares immutable
tmp (smallsort.rs:556). Changing the fixture to mutable tmp would provide unit
permission while losing that correspondence. Adding full permission as a premise
or weakening the full-storage post is not permitted. The historical address-taken
patch fixes traversal continuation, not half/full permission; importing it would
neither solve this problem nor respect this phase's allowlist.

There is no established route to full tmp storage under the current immutable-
local model. This earlier caller blocker means the intended missing-init negative
has not been exercised. The independently proved helper is conditional on its
resource precondition; its successful body is not a caller lifecycle proof.

## Pointer and refinement boundary

The draft's `_tmp_shared as *const T` uses the existing supported Cast path in
refinement_checker.ml:2100-2102,2654-2659 instead of unsupported MIR RawPtr.
But precreate_ref/create_ref (bin/rust/aliasing.rsspec:77-90) return a reference
pointer with only ref_origin equality to the original. The recovered heap cell
is *tmp at the original pointer. ptr::read lowers to Ast.Deref of the actual
source pointer (vf_mir_translator.ml:2396-2400). No supported permission rule
establishes a full read at the saved child pointer from that original heap cell.
Logical ref_origin normalization is not a runtime pointer operation. A successful
refinement check alone cannot justify this substitution.

The original addr_of!(tmp) preserves owner provenance but the unchanged refiner
rejects RawPtr. Actual ManuallyDrop::into_inner (library/core/src/mem/manually_drop.rs:
202-205) also reads from &raw const slot; that callee has no established route
in the pinned profile. No pointer rewrite is applied. Adding RawPtr support or
an alias/permission bridge requires a separate semantic/trust decision.

## Actual insert_tail all-path routes

Actual source library/core/src/slice/sort/shared/smallsort.rs:542-577 is unchanged.
Saved MIR from run37417173472 is historical evidence for that extractor/profile,
not a fresh export of this diagnostic. Its compiler-mir.log:1810-2100 shows:

| Path | Exact runtime control | Required full resource recovery | Frozen-profile feasibility |
| --- | --- | --- | --- |
| First comparison true | bb1 call_mut -> bb2 -> bb3 read -> bb5 new -> bb6 deref -> bb7 guard | End both comparison borrows; return full current tail/sift cells and current F before tail.read | Normal recovery helper works in a natural-block fixture, but actual source lacks that block; previous strict-cut prefix used a different, excluded profile |
| First comparison false | bb1 -> bb2 -> bb4 -> bb19 return | All n initialized current cells, ONE T.own per element, F/thread/types/frame; close all debts/tokens before return | Source ghost recovery after the if is bypassed; no established source-exact scope route |
| First direct panic | bb1 -> unwind continue, before tmp/guard | Same full range/F resources on unwind, no sortedness condition | Continue lowers to ReturnStmt(unwinding); trailing recovery is skipped and there is no Drop cleanup edge |
| Late panic (future phase) | bb13 -> bb20 Drop(guard) -> bb21 resume | Fill current gap, return full range, release held ref and merge tmp storage | Different local-Drop profile cannot be silently imported; held-reference release remains open |

The baseline fixture creates a real inner Rust block with let_lft, then runs an
ordinary nonghost-only recovery lemma after it. The source's first comparator is
inside the outer unsafe block, followed by the false arm and tail.read. Exporter
preprocessor.rs:132,226-245,543-565 only recognizes let_lft in a real Rust block.
Translator:2473-2492 lowers direct Continue to ReturnStmt, Cleanup to GotoStmt.
Verifier verifast.ml:2672-2680 returns the reserved block lifetime fraction and
frees locals on return, but skips trailing ghost statements. An auto-lemma cannot
call nonghost-only end_lifetime/borrow_end/close_frac_borrow (verify_expr.ml:
381-386,3136-3141; lifetime_logic.rsspec:76-79,122-125,280-283).

Guard.src is reference-derived in saved MIR: bb6-7 creates &ManuallyDrop<T>,
derefs to &T, reborrows and converts that shared reference to raw const pointer.
Replacing it with an owner-address pointer would not discharge that provenance
obligation. Actual Drop's prior verified summary is conditional on fractional
src bytes and ONE ownership sequence; it does not release held_ref or restore
full tmp storage, and belongs to a different source/tool profile.

## Decision boundary

NO-GO for actual insert_tail integration under the frozen phase profiles. A
normal bookkeeping success does not establish full immutable tmp storage,
pointer refinement/permissions, source-exact scope placement, false-return recovery or first-panic recovery.
No callback integration or AST routing is implemented.

Choices requiring the owner's next decision:

1. Review the immutable-local half/full storage obligation and an admissible
   source-faithful resource model before attempting another MD lifecycle gate.
   Separately authorize a narrowly specified RawPtr refinement-support experiment,
   with unchanged source pointer semantics, independent positive/negative
   differential MIR/refinement tests and an explicit trust/admissibility review.
   This only addresses the diagnostic owner-pointer blocker; it does not solve
   real guard.src or direct unwind.
2. Separately design/review source-exact borrow scope and direct-unwind routing
   (candidate in BORROW-RECOVERY-DESIGN), including full normal/false/panic posts,
   preserved runtime/cleanup edges and a rejection/regression gate BEFORE
   semantic implementation. Also justify reference-derived guard.src resources.
3. Keep these milestones and choose a simpler target such as generic swap or
   sort4, or investigate another existing-semantics proof route. This is a new
   phase, not an automatic continuation.

## Archived execution scope and tool profile

The following was moved from the previous STATUS checkpoint when the owner
approved the sort4 phase. It records the completed phase's permission boundary;
its patched profile is not authorized for the new phase.

This bounded phase was explicitly authorized and has reached its stop boundary.
The following records its contract; it does not authorize another phase.
No new verifier semantics, callback integration or full insertion proof is part
of it. Autonomy covers routine fixture/spec/audit fixes and hosted iterations
within these boundaries, then stops for an architecture decision.

1. Review and isolate same-reference `recover_single` bookkeeping. Prove the
   coefficient/resource conditions; retain unrelated baseline controls without
   the new helper. State expected proof stage/predicate/location for each case.
2. Resolve the raw-pointer provenance/refinement blocker without weakening posts,
   bypassing the checker or changing the target's pointer semantics. If that
   requires changing tool semantics/support, STOP and present the decision.
3. Once statically justified, run the seven-case minimal ManuallyDrop gate on a
   NEW pushed SHA, inspect all evidence, and record only the established scope.
   Use the separate unchanged-release baseline control when relevant.
4. Document applicability to actual `insert_tail`: normal true path, false early
   return and first direct panic must have explicit full storage/ownership
   recovery routes. A natural-block fixture alone is insufficient. Close this
   phase with a go/no-go report; do not implement a new AST scope/routing feature.

Allowed tool profiles in this phase: unchanged pinned release 26.09
(`verifast_borrow_recovery`), and the EXISTING `manually_drop_only` profile
(`verifast_borrow_recovery_manually_drop`), with no patch expansion:

- VeriFast source `809de4596839b739dd999f9e462242c835e3af46`;
  Rust `nightly-2026-02-05`.
- Sole patch `verifast-manually-drop-ref.patch`, SHA-256
  `5500204aadd0ea0a2996d63d064160185457b6d337782aa4300c11272ab450cc`.
- Translator input SHA-256
  `7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803`;
  output `60ece6e90f4dd3c623a99ea31feebb3210359daa38850255332118b2316eac39`.
- Parser, kernel, prelude, memory model, exporter and refinement checker remain
  unchanged. Retain existing dependency/binary/source audits. The full historical
  patch chain is evidence, NOT a default fallback or phase permission.
