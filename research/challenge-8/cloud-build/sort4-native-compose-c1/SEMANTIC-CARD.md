# Native entry to first comparator: experimental composition card

Status: preimplementation design for independent review. This card grants no
tool-profile acceptance and records no new proof result. The assigned
select-sort4 session begins 2026-10-10 00:34:15 UTC; main deadline 02:34:15,
absolute finishing deadline 03:04:15. The current `WORK-POLICY.md` revision
was read in this worktree at session start; its source revision will be pinned
with the next checkpoint.

## Actual obligation and useful boundary

The actual std source is
`library/core/src/slice/sort/shared/smallsort.rs`, pinned blob
`40939f922bcb6fdc7ee0d30427fa861827043827`. The source caller
`small_sort_general_with_scratch` has the first `sort4_stable(v_base,
scratch_base, is_less)` call at line 254; `sort4_stable` has the first
comparison `let c1 = is_less(&*v_base.add(1), &*v_base);` at line 620.
Fresh 46bb proves the native source/F/current-thread resource subset and
opaque scratch frame; fresh 65d6 proves an actual-source bounded c1 first
callback under a stronger raw contract. Those are separate theorems.

The next useful theorem is an internal, callable *c1-only* function containing
the exact first comparator operation and its checked lifetime/ownership
recovery, with the complete source array/F/thread contract but no destination
permission. It splits source4 from the unchanged tail, recovers and rejoins
the four **CURRENT** values and owners on both outcomes, then appends them to
that tail. Its normal and direct-Continue unwind posts return the complete
current source array/owners, current comparator cell/`F.own`, and thread
token. Stock `produce_type_interp<T/F>` occurs inside this real helper and
both chunks are explicitly leaked after recovery on both outcomes. It neither
reads nor writes `dst`, and its contract does not mention destination storage.
All four source cells and both callback outcomes are retained. No equality to
entry values is assumed after the callback. The unchanged-tail claim requires
an explicit checked assertion of the tail value/owner frame on each outcome;
without it, only the existential CURRENT full-array post is credited. The
checked `recover_pair` and
`join_four_owned_cells` helpers must verify before their caller in the same
exact source unit. The helper's ordinary executable Rust body terminates
after c1; therefore its verified contract can legitimately be used by a
separate caller. The prior AST-truncated actual `sort4_stable` cannot be used
as a callable summary and remains unchanged.

A separate native diagnostic keeps the exact
`small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T,&T)->bool>`
signature and its generated complete safe-entry contract. It copies the
original read-only `len`, `v.as_mut_ptr`, `len/2`, and scratch-pointer
operations with byte-exact header/statement offsets against the pinned full
std source, then explicitly checks a restricted non-ZST `len>=8` domain
before calling the verified c1-only helper. This is an artificial diagnostic
branch, **not** the original caller CFG, scratch abort guard, inline-const
selection, or actual sort4 call. Its positive result would show that the
native source4/F resources plus the helper's stock type interpretation
can enter and exit a checked c1 callback while restoring the complete native
normal/unwind return and leak posts. The entire original `MaybeUninit<T>`
scratch array/owners remain opaque and framed through the call. The helper's
raw pointer `dst` argument, if retained solely for source signature mapping,
must carry no T destination heap premise and must not be dereferenced.
The current source draft has no `dst` parameter at all and uses an internal
`len` argument solely to carry the native tail frame across direct unwind;
this is an internal interface, not the actual sort4 signature.

Domain: arbitrary safe native `v`, `scratch`, F and T at function entry;
the diagnostic c1 operation executes only in the stated `len>=8 &&
size_of::<T>()>0` subset. Positive size is explicit and excludes ZST from
the callback proof; the standalone native resource lemma continues to admit
ZST. No `Copy`, purity, callback nonpanic, or entry-value preservation
restriction may be added. The actual sort4 and caller full generic/ZST
obligations stay open. The helper's safety proof must retain all source
pointer provenance/limits and owner resources; a numerical pointer equality
cannot generate permission.

## Semantic boundary and source applicability

Prefer a proof-source-only internal helper and frozen existing translator
profile. If a narrow frontend/projection repair is necessary, it is a new
experimental semantic component: write its exact source/MIR/AST identity,
falsifiable rationale, trust assumptions and affected regression gates here
before implementation, then obtain independent review. The patch may only
recognize the pinned helper and first direct-Continue comparison; it cannot
change stock contract semantics, memory/alias rules, kernel, refinement,
unwind, leak or dead-code checks. Default-off behavior and the existing
whole-sort4/c2 mandatory refusals remain unchanged. An AST transformation
must preserve every reachable prefix path and all original outcome posts;
it must not replace the complete `sort4_stable` proof by a c1 summary.

Exact source binding must compare the helper's single executable comparison
with the pinned original c1 expression and operand order, and separately
retain the previous full `sort4_stable` source/MIR/AST certificate for the
actual bounded theorem. Both normal and readonly typed MIR must show the
single `FnMut::call_mut` from source cells 1,0 with direct `Continue` unwind,
no cleanup/Drop path elision. Normal and unwind proof AST/trace must show
debt close, strict lifetime exit, pair recovery and four-cell join before
their respective posts; same-unit callee verification precedes native use.

## Falsifiable test and decision

Positive: source-linked c1-only helper VF0 with full CURRENT normal/unwind
posts, and native diagnostic VF0 with complete generated normal/unwind posts,
return, leak and intact opaque MU frame. The stock callback and helper
verification logs, paired MIR, refinement, and source/AST mapping are
required evidence. One negative removes a comparison-debt resource and must
fail first at the checked recovery precondition after target entry. Separate
false normal/unwind posts must fail at their respective post obligations;
source owner loss must fail at the four-cell join or native post, not in
setup. Mutated source operands, call count, unwind edge, or unbound C2
annotation must be refused by admission. Existing C1 strict controls and
default-off full-target behavior remain regression gates when the semantic
overlay changes; tests are isolated so unrelated helpers cannot block the
baseline.

If the helper passes but native entry fails, classify the first source/owner/
type/frame/post blocker and repair only within the scoped profile. If the
native theorem passes, the next work is actual caller CFG guards and eventual
whole `sort4_stable` result; this result alone proves neither. If a new
ownership bridge, MU inverse, ZST model, or unrestricted whole-function
summary is required, stop and return the material decision to the owner.

Compilation, extraction, refinement and proof run only in the assigned
Cloud Build lane with exact proof/infra/tool identities. No Actions dispatch,
local toolchain execution, std runtime edit, or external publication.

## Build4 frozen input and first semantic proposal (rejected)

Cloud Build `0904f144-a6dd-4ebe-b57c-79c2e2dc3433` captured the **original,
unmodified** helper `Func` before any semantic overlay. The complete exact
serializer output is `cases/positive/fixture/c1-original-func-ast.ml` in the
hash-verified archive at `/tmp/native-compose-0904f144-read/allprooflogs/cases/sort4-native-compose-c1`.
Its SHA256 is `64c01593d890907756c2e707e09adb9da80c6a1d0967a6720d2200defacf8b06`;
the original immutable `Marshal.No_sharing` MD5 is
`f9e8dd5ea212287b36fa0beddd896528`. The verified source SHA256 remains
`28716b042293c4b5211d5696464696fa7da073ca15301a6002b62f3813d3497e`.
Normal and readonly complete helper MIR SHA256 values remain respectively
`0dc4d60b62343cb816326b4cf229581081f4e7ff906559cdc2448f14853be3b0`
and `362db0d6d413be96c526407fb6781498cdde8ff8a68b8d064eb3ec4a1a0cc720`;
native complete MIR SHA256 values remain `1163da55264497d8b57186aa3974a1ab2087e1439177e0aecc875b9c3479d674`
and `c87004838fcef0d3b575c57bb1758ca06a585df725733d584322e0de49e7d666`.
The saved paired-MIR structural classifier passed, including one source-line-199
FnMut F/(&T,&T), ordered element 1 then 0, direct Continue, no cleanup/Drop,
and all eight callback locals' declaration/live/init/dead/address inventories.
The readonly MIR has exactly two runtime call terminators before exit:
`std::ptr::const_ptr::<impl *const T>::add` for source `v_base.add(1)` at
line 199, then `FnMut::call_mut`. Both MIR terminators say `Continue`; the
stock translator represents the pointer `add` as a pure AST `Operation Add`
with no outcome switch, so the proposed patch does not erase or alter its
edge. This existing intrinsic lowering and the complete pre-callback AST
must be pinned and reviewed. The positive verification must prove the
pointer operation's existing safety obligations before reaching FnMut.
The AST diagnostic still exits 2 only in the unrelated whole-module
`MergeFractionsStmt` serializer; full VF with capture disabled still first
refuses at the source marker line 189. Capture is not proof credit.

The rejected **experimental, default-off, helper-only** overlay would act on the
complete translator-created `Ast.Func`, not on its contract or source. It
requires opt-in `SORT4_NATIVE_C1_COMPOSE=1`, exact source SHA, signature line
135/path, existing strict/HRTB opt-ins and target, the pre-overlay immutable
AST MD5 above, and the four full MIR hashes supplied as admission pins by the
runner. (The translator checks the source/AST, while the Cloud runner checks
MIR.) It refuses duplicates or a changed body. All non-target bodies pass
unchanged. The captured target AST shows exactly one callback at line 199 with
`returning` and `unwinding` clauses; the latter has a direct
`ReturnStmt(unwinding())`. The callback marker at lines 188–198 is a pure
source-written block with exactly four inner blocks: debt close line 190,
`recover_pair` line 191, `join_four_owned_cells` line 192, and full CURRENT
`assert`/`array_join`/`foreach_append`/T/F leaks lines 193–197. The normal
tail already has the corresponding source steps at lines 200, 204–210.

That proposal would remove only the **callback marker command** (which is intentionally
undefined), move the eight exact callback temporary declarations in their
original order from the function-top declaration list to the beginning of the
unique `'cmp` block, and split the four existing source-written blocks: debt
close goes into the callback `unwinding` clause, followed by a goto to a new
epilogue label outside `'cmp`; the three recovery blocks run at that label,
then the original `ReturnStmt(unwinding())` runs. It will retain the original
normal callback clause and the complete normal tail byte-for-byte at AST
statement level. The production translator has **no active strict-cut
handler**; its `SORT4_STRICT_LFT_CUT` environment option is presently only a
gate in the capture hook. The first proposal's cut at line 202 therefore
cannot borrow an existing semantic implementation. The narrower revised
proposal retains the original lexical `'cmp` `BlockStmt` close at line 203 and
its original `GotoStmt("31")` inside the block. The exact source
`end_lft_binding::<'cmp>()` command at line 202 is consumed as a guarded
Noop: there is no resource or runtime operation between that command and the
lexical block close, only the existing goto. Normal recovery begins at the
original label 31 at line 204 outside the block; the new unwind epilogue is
likewise outside. Independent review **rejected** this Noop treatment: the
source marker has no definition in the frozen profile, and Noop would delete
its lifetime-end obligation. This design is retained only to record the
failed approach and must not be implemented. The old isolated strict-cut
profile uses both a translator marker and a `src/verifast.ml` escape check;
neither is present in the current production profile. Its transfer would be
a new trust change outside the authorized translator-only overlay. Any later
approved design must show that both callback outcomes leave `'cmp` under a
checked strict scope before recovery and full CURRENT normal/unwind posts.
Every reachable helper path must traverse the moved declarations exactly
once before their only uses, preserving their relative declaration order and
the original Rust MIR StorageLive/init/dead sequence; each AST declaration is
uninitialized, non-address-taken, and occurs once after transformation. The
eight exact normal MIR locals are `_33`–`_40`, readonly `_7`–`_14`; the AST
names are `$_33`–`$_40`. The remaining function-top declarations, source
steps, all other callbacks, and native function remain unchanged.

Any later separately authorized overlay must inspect structural AST types and exact locations before
rewriting, count each moved declaration, marker, callback, cut and original
return once, and refuse any extra callback or unknown control/cleanup branch.
It must log original/rewritten immutable fingerprints, before/after inventory
counts, exact source/MIR pins and normal/unwind recovery order. No assumption,
new ghost resource, skipped branch, disabled leak/unwind/deadcode is allowed.
The current frontend-only profile permits no kernel/parser/spec change. A
future strict-cut profile would require its own authorization and review
before these tests. First falsifiable Cloud positive: all
setup/refinement support stages zero, helper VF0 with both full CURRENT posts,
then native VF0 with its original complete generated normal/unwind posts and
opaque scratch frame. A first refusal elsewhere is diagnostic only and will
be classified before any further edit. A second reviewed overlay would be
required for a new source shape or expanded domain. The captured AST and this
exact proposal were independently reviewed; implementation is on hold at the
strict-lifetime dependency, and Build4 grants no proof credit.
