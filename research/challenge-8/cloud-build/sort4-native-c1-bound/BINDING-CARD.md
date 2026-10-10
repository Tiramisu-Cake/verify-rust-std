# Exact native C1 binding — DRAFT / IMPLEMENTED / NOT_RUN

This is a review contract for a new isolated translator mode, not a proof or an
accepted tool profile. The callback-free prepared diagnostic passed strict
entry and its native resource assertions, then stopped at the reverse
reference-own preparation before an actual callback call. The only implementation file is
the isolated VeriFast worktree's
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`, starting from
HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb` plus the existing
capture-only translator (`86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544`).
The frozen C4 translator is `1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`;
its C4 bound mode remains untouched and still admits only `sort4_stable`.
No kernel, parser, alias, arithmetic, MU, prelude, refiner, or general inference
rule is proposed here.

## Exact obligation and evidence

Prove the native automatic safe-reference contract of the **internal**
`small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>`
candidate, conditional on its runtime `size_of::<T>() != 0` and `len >= 8`
path, through its **actual first** `is_less(&*v_base.add(1), &*v_base)` call.
The callback must have normal and direct-unwind outcomes. Both must recover
CURRENT source T owners and values, F/thread, the opaque scratch
`MaybeUninit<T>` array and owners, automatic lifetime tokens, unit return,
allocation/free and leak obligations. The first four source cells are split
from the automatic native source permission; the untouched tail is rejoined.
The callback may mutate F or panic. Source and scratch input snapshots cannot
stand in for CURRENT resources. The positive-size path is a separate internal
condition; selected sort4 with `len == 8` and zero-sized T does not imply it.
External `v.as_mut_ptr()`/`scratch.as_mut_ptr()` method summaries, checked-add
guard/abort, caller branch and call edge remain outside this component.

Pin the complete verified source SHA-256
`7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742`,
original runtime source SHA-256
`7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1`,
normal MIR `8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4`,
readonly MIR `bde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa`,
and the complete fresh original pre-AST
`18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5`
(Build `081275a9-032a-4053-a088-c173f12f05c9`). This pins all declarations
and the full normal/unwind contract, not merely a selected call substring.
The previous capture's artifact is
`/tmp/native-opaque-081275a9-review/allprooflogs/cases/sort4-c1-current-recovery/supplied/native-c1-capture-preast/fixture/native-c1-capture-pre-ast.ml`.

## Admission before proof AST changes

Use a new malformed-value-rejecting, default-off, exact-one-body bound opt-in,
mutually exclusive with native capture, C1–C4 old modes, AST_SCOPE and other
controls. Require `SORT4_STRICT_LFT_CUT=1`, full unwind/dead-code/leak checks,
the exact source hash and one body named `small_sort_general_with_scratch`.
Require the same exported typed MIR pair and refinement result; inspect the
MIR call graph and StorageLive/StorageDead inventory in addition to the hashes.
In particular require one compiler `FnMut::call_mut` at source 210:21–92,
receiver F and tuple arguments derived from pointer operands 1 then 0, one
normal result and one direct unwinding successor, one `__vf_sort4_first_unwind`
marker at 194 and one `end_lft_binding::<'cmp>()` cut at 212. Reject any
unexpected call, marker, different successor, extra function, or changed
source coordinates. The complete MIR block/local count and exact storage
edges require independent review of the pinned MIR artifact before code;
the captured AST alone cannot certify them.

Before rewriting, emit the complete original declaration and require the
pre-AST hash above. Independent static inspection of that artifact found 134
top-level statements, the first 76 being local declarations. Top-level local
index 2 is `_5: &'erased [T]` for `v.len()`; it is assigned at root index 77
and last used by `ptr_len` at index 78, before the `size_of` switch at 79.
Top-level indices 52–59 are callback temporaries `_55.._62`; exactly seven
outer local declarations contain eight `InferredTypeExpr` occurrences (`_5`,
`_55`, both elements of `_56`, `_57`, `_58`, `_61`, `_62`). `_59` and `_60`
are raw pointers without inferred region. Keep bool `c1` at root index 51
outside the lifetime child. Check these types, names, untouched initializers,
address-taken flags, all later uses and source spans; do not rely on a count
alone. The sole `'cmp` block is root index 112, with 35 child statements,
one `TypeWithTypeidDecl('cmp, cmp_k)` and initial empty `locals_to_free`.
Within it the marker is child index 21, the argument preparation is 22–30,
the actual `FnMut` `SwitchStmt` is 31, debt close is 32, regular cut is 33,
and original goto is 34. Reject deviations, including a changed normal or
unwinding clause. The marker has **four** checked cleanup blocks: debt close,
pair recovery, first-four join, and tail/source/MU/F/type rejoin. Do not use
the old C4 three-block matcher or omit the fourth block.

## Bounded transformation to review

`_5` stays in its original outer declaration. Fresh callback-free preparation
passed strict entry with this same `v.len()`/`size_of` prefix, so there is no
observed `_5` failure to justify a scope rewrite. The pinned MIR still checks
its StorageLive in bb0, StorageDead in bb1, and no later use. If a fresh bound
run reveals a named `_5` failure, it requires a new review rather than an
automatic extra relocation. Root label 76 and all source branches remain.

As in the reviewed C4 mechanism, move exactly callback locals `_55.._62`
from the outer declaration list into the `'cmp` child, preserving their
compiler-derived types, order, initialization, address-taken and free semantics.
Insert the strict lifetime-scope entry for `'cmp`; keep the checked end cut
at its original source boundary. The ordinary normal path must execute the
real call, debt close, strict exit, `recover_pair`, `join_four_owned_cells`,
tail rejoin and complete native post. The direct unwind branch must close the
same debt, leave the lifetime child, execute the **entire four-block** marker
cleanup and return the compiler's `unwinding()` outcome. The direct unwind
must not fall through normal comparison code. Check every generated goto's
target and all local frees after relocation; an empty captured `ref []`
`locals_to_free` is not evidence that cleanup is unnecessary.

Use the existing source- and MIR-checked HRTB path for exactly `F`, `T`, one
late-bound `'cmp`, and compiler-derived
`<F as FnOnce<(&'cmp T, &'cmp T)>>::Output = bool`. Register that equality
only at the unique actual call; require one normal assignment to `c1` and
one direct unwind. Never attach it to other native calls, derive it from the
source comment alone, assert a generic `Output=bool` axiom, or assume a
callable summary for whole sort4. The post-rewrite AST must be saved and its
complete contract compared to original: only certified declaration scope,
projection registration and unwind control placement may change. No source
assertion, full automatic post, leak or checked helper may disappear.

## Regression and decision gates

First run an unbound/default-off control on the same source: it must retain
the original strict-entry refusal and exact captured AST. Then run the new
bound positive only after callback-free preparation demonstrates its input
resources. Require all same-version helper bodies to pass before the native
body and fresh normal **and direct unwind** verification with full native
posts/unit/free/leak. Add localized controls for false normal post and false
direct-unwind assertion; they count only if reached after the actual call at
the intended predicate. Exact-source mutation, extra body, altered
call/marker/cut, missing fourth cleanup and mixed-profile controls must refuse
at admission. Retain frozen C4 regression independently. If `_5` scope,
reference-own identity, borrow debt, pointer provenance, arithmetic, MU or
callback `Output` cannot be closed with these pinned mechanisms, report the
first actual failed obligation and return the relevant general semantics to
its owner. No C1/C4 proof credit follows from this card or capture alone.
