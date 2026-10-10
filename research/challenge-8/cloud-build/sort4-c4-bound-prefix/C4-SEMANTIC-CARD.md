# Actual C1 → C2 → C3 → C4: conditional bounded projection

This card prepares the next prefix only if the exact C3 bound profile is
proved on Cloud and independently reviewed. It authorizes no C4 dispatch or semantic translator change
by itself. Owner `select-sort4`; source is the actual `sort4_stable` in std blob
`40939f922bcb6fdc7ee0d30427fa861827043827`. The existing C3 capture
source/pre-AST/MIR pins do **not** admit a C4 proof, because the new annotation
changes the source and ghost MIR.

**Obligation.** Preserve the actual first three callback outcomes and extend
the bounded projection through the fourth source comparison
`let c4 = is_less(&*d, &*b);`, its normal lifetime exit and its direct unwind.
Stop immediately after C4's CURRENT recovery and four-cell rejoin, before the
first `select_unpredictable`. This remains a diagnostic prefix, not a callable
whole-sort4 summary or credit for C5, selects, copies, or the caller.

**Hypothesis.** After C3 rejoins the four CURRENT cells, the unchanged
source-derived pointers `d` and `b` designate distinct owned cells in the two
halves. The preceding C3 target must first prove the same-source-version `split_selected_four` exposes
all four individual cell and `T.own` resources. A fourth comparison debt uses
only `(d,b)`; `(a,c)` is its untouched frame. On normal return or direct unwind,
`recover_pair(d,b)` produces fresh existential CURRENT values at those cells,
then `join_selected_four(v_base,t,c1,c2)` restores the complete array and
`foreach` ownership in physical order. No pointee-value relation to values
before C4 or to the comparison Boolean is presumed.

| c1 | c2 | C4 `(d,b)` indices | frame `(a,c)` indices |
| --- | --- | --- | --- |
| false | false | `(3,1)` | `(0,2)` |
| false | true | `(2,1)` | `(0,3)` |
| true | false | `(3,0)` | `(1,2)` |
| true | true | `(2,0)` | `(1,3)` |

The indices follow the actual source expressions `a=v_base.add(c1 as usize)`,
`b=v_base.add(!c1 as usize)`, `c=v_base.add(2+c2 as usize)`, and
`d=v_base.add(2+(!c2 as usize))`. The left and right halves are disjoint;
each of the four offsets is within 0..3. This arithmetic establishes bounds
and distinctness, while permission comes from the real array/`foreach` split,
not numeric pointer equality. The existing `selected_four_limits` ghost call
must stay before the original pointer setup so the runtime `.add` proof
obligations remain discharged. The C4 annotation repeats the source-shaped
limits and split after the C3 join; it does not move or recalculate pointers.

**Domain and posts.** Use the original four-cell source/F/thread/type and
positive-size T domain, original optional destination contract, and unrestricted
`F: FnMut(&T,&T)->bool`. Retain the complete original CURRENT normal and every
reachable direct-unwind source/F/destination post, unit return, leak check,
dead-code check, and refinement. C1/C2/C3 direct unwind skips C4; C4 direct
unwind closes its debt, exits the strict lifetime, recovers `(d,b)`, rejoins
four cells, and reaches the same original unwind post. The `c4` Boolean and
`a,b,c,d,c1,c2,c3` must remain available outside C4's strict child scope.
Verify C4's compiler-derived HRTB `FnOnce::Output=bool` independently of
C1/C2/C3. Preserve exact allocation, initialization, address-taking and
deallocation effects on each path. No Copy/Freeze/purity/no-panic premise,
kernel/parser/spec/memory/refinement change, runtime/signature edit, or
assumed ownership bridge is allowed.

**Capture and admission gate.** Begin from the exact reviewed C3 experimental chain. The
minimal source edit inserts [`C4-ANNOTATION.rs`](C4-ANNOTATION.rs) immediately
after C3 normal `join_selected_four` and before the unchanged C4 call. It adds
`/*@ let_lft 'cmp4 = cmp4_k; @*/`, the fourth direct-unwind marker, and the
explicit `is_less` type/lifetime arguments. A capture-only translator mode
parses the exact named `cmp2`, `cmp3`, and `cmp4` declarations into distinct
placeholders, checks their order and single use, writes the entire original
pre-AST, and refuses before proof. Save exact annotated-source SHA-256, full
normal and readonly MIR records, pre-AST SHA-256, source/runtime ghost-strip
identity, all five callback sites, eight selects and four copies. Review the
new C4 callback locals, result Boolean, unit ghost locals, liveness and AST
allocation/free positions afresh; no C3 local numbers or line offsets are
presumed. Pin all fresh inputs before any C4 bound translator path. Default-off
C3 replay and mandatory unbound refusal remain independent gates. Reject
mixed experimental opt-ins and source/pre-AST mutants.

**Falsifiable bound test.** Only after capture review and same-version helper
proof, construct C1/C2/C3/C4 sibling strict scopes. C4 normal and direct unwind
must both complete the debt/recovery/join sequence above and prove the full
original posts. A positive requires full bounded VF0 with original return and
leak checks; same-version helper proofs precede the target. C4 normal/unwind
missing-close controls must fail at the debt/recovery obligation; normal/unwind
omitted-join controls must fail at the original CURRENT four-owner post. A
normal false-post and reachable C1/C2/C3/C4 unwind false-assert controls must
fail at their intended paths. Setup, parser, unsupported-operation or unrelated
helper failures count only as setup failures. Inspect first failing stage,
predicate and location in complete Cloud logs before crediting any result.

**Outcome.** Positive bound and controls permit proposing a separate C5/select
step within the assigned phase and remaining account; they do not prove the
whole function. A localized resource or correspondence failure calls for a new
exact SHA and re-review. A new trust requirement needs a separate written
rationale and explicit admissibility review before implementation.

Independent GPT-6 Luna source/design review (2026-10-10): conditional GO
after full C3 verdict. Actual operand order `(d,b)` and all four frame cases
match source. Fresh C4 MIR/pre-AST/local/allocation review remains required;
no C4 runtime/proof claim follows from this preparatory card. Main accepts
this narrow design; exact capture delta will be separately reviewed.
