# Selected Freeze branch and length-bound interface

**Cloud-only source-bound diagnostic design.** This card defines the intended
selected-branch fixtures in `selected-branch-cases.rs`. It carries no proof
result and does not authorize verifier execution outside the existing
caller-bound session. Static source identities below are admission inputs;
the fixture must be re-bound to exact extracted source/MIR before Cloud use.

The selected source identities are:

| Source | SHA-256 |
| --- | --- |
| `library/core/src/slice/sort/stable/quicksort.rs` | `4a41df6bc7c4e0a6fcb655fde9bf73ed62f3a675ca805f2f766919ce249d8f4c` |
| `library/core/src/slice/sort/shared/smallsort.rs` | `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1` |
| `library/core/src/slice/sort/shared/mod.rs` | `fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8` |

The source path is the actual stable quicksort base guard, then the actual
`StableSmallSortTypeImpl` Freeze specialization, then its same-argument call
to `small_sort_general_with_scratch`. Only that selected Freeze theorem is in
scope. The general quicksort signature remains unconstrained in the runtime
source; this diagnostic wrapper adds `T: FreezeMarker` solely to express the
selected branch. It establishes no dispatch for an unconstrained caller, no
whole-quicksort theorem, and no unrestricted safety restriction.

## Closed source inventory and proof boundary

Each extracted case must contain only this source-linked inventory:

1. The real stable `quicksort` initial loop/base-case shape, with its actual
   `len <= T::small_sort_threshold()` call and `T::small_sort(v, scratch,
   is_less)` transfer. The diagnostic return at the non-base edge cuts off all
   later quicksort work.
2. The actual `StableSmallSortTypeImpl` declarations, the selected
   `impl<T: FreezeMarker>` method bodies, and
   `SMALL_SORT_GENERAL_THRESHOLD: usize = 32`. The threshold body has a
   resource-preserving ghost contract (`thread_token`, normal result 32,
   thread-token unwind post) matching the exact-body threshold probes. The
   blanket fallback implementation is deliberately absent from this selected
   extraction; its default result 16 is checked in the separate two-impl
   threshold admission probe.
3. The actual selected `small_sort` body forwarding the identical `v`,
   `scratch`, and `is_less` to the helper.
4. The actual helper prefix through its first `sort4_stable` call boundary:
   `len < 2` early return; evaluated `scratch.len() < len + 16` and abort;
   `v.as_mut_ptr()`; `len / 2`; `scratch.as_mut_ptr() as *mut T`; the original
   const/length branch order; and the native-resource boundary assertions on
   the selected `len >= 8` branch. The return at that boundary provides no
   callee summary or post-boundary credit.

The positive helper asserts `ptr_len(v) <= 32` at entry. That is an obligation
of the *generated helper precondition*, not a source assumption or hand-written
ownership bridge. Main's narrow native interface protocol must add only this
pure conjunct to the generated preconditions for the exact selected method
and helper. It must preserve every original source/scratch/F/thread/lifetime/
type precondition, and preserve the generated normal and unwind post AST
exactly. The selected method receives the same conjunct so it can discharge
the helper precondition. The actual guarded caller must prove the selected
method precondition from the actual threshold post and branch condition.

No `len >= 8`, nonzero-size, ZST return, initialized-`T` scratch permission,
callee summary, or extra length precondition is supplied. The helper's own
branch establishes `len >= 8` only where the native resource boundary is
checked. `len <= 32` does not establish that branch or nonzero size.

## Cases and falsifiable gates

- **Positive selected path:** actual threshold call returns 32; the guarded
  caller proves `len <= 32`; the selected trait method forwards the same three
  arguments; its generated interface proves the helper's `ptr_len(v) <= 32`
  precondition; then the helper reaches the actual first-call boundary with
  full native source, opaque `MaybeUninit<T>` scratch, callback, thread, type,
  and lifetime resources. Require full generated normal/unwind posts, local
  free/leak checks, source/MIR identity, and paired normal/read-only MIR plus
  refinement.
- **False bound control:** put `assert len <= 31` inside the actual guarded
  base branch before `T::small_sort`. It must be rejected at that assertion;
  length 32 is admissible under the actual threshold. A method-binding,
  frontend, setup, or unrelated resource failure is not this negative.
- **Missing source-array control:** inside the same reachable guarded branch,
  derive the native source `array::<T>` resource from the actual `v` parameter,
  then deliberately leak only that array before calling
  `T::small_sort`. The call must fail at its exact selected-method source-array
  precondition. Keep the source `foreach` ownership, all scratch resources,
  callback resources, thread token, and type/lifetime resources. This control
  rejects an accidental assumption that pointer equality or the length bound
  manufactures source authority. It is a diagnostic negative only.
- **Source admission:** refuse before verification if the extracted caller,
  selected impl, helper prefix, or source/MIR method binding differs from the
  pinned identities or expected call graph. The threshold probe that includes
  both impls remains the separate fallback-16/selected-32 admission control.

The translator's generic trait-implementation matcher is a separate trust
gate: the selected-only case cannot establish that unconstrained quicksort
dispatches to the Freeze impl. Main must cross-check the compiler's selected
impl/body against the two-implementation threshold probe and actual MIR call
edges. If the compiler cannot express that selected binding, this fixture
qualifies at most the explicitly Freeze-qualified diagnostic theorem; it gives
no caller-transfer credit for generic quicksort. No kernel, ownership,
MaybeUninit inverse, parser, memory-model, or general specialization change is
introduced by these source cases.

## Translator candidate: conditional exact-body interface

This trust/admissibility rationale is recorded before the selected-branch
translator patch. The base is the threshold candidate pinned by
`STABLE-THRESHOLD-BINDING-PINS.json`; the selected-branch patch is a distinct,
default-off candidate. It is enabled only in the named Cloud phase with the
separate `SORT4_SELECTED_BRANCH_INTERFACE=1` opt-in, and rejects overlapping
threshold-binding mode. It also requires the runner-owned
`SORT4_SELECTED_COMPILER_BINDING_VERIFIED=1` gate. The runner may set that flag
only after exporter evidence validates the actual Freeze-qualified caller
TypingEnv and selected impl DefIds; no handcrafted TypingEnv qualifies. Its
source admission pins the three independently extracted case digests in
`SELECTED-BRANCH-BINDING-PINS.json`. Those are
reproducible fixture-source digests, not Cloud proof results; there is not yet
a Cloud source/MIR pair for these cases.

The mode admits a closed four-body inventory: `selected_freeze_basecase`, the
selected `StableSmallSortTypeImpl::small_sort_threshold` impl body, the
selected `StableSmallSortTypeImpl::small_sort` impl body, and
`small_sort_general_with_scratch`. For the selected impl method and helper
only, it adds the pure precondition conjunct `ptr_len(v) <= 32` to the
generated native precondition. It retains all generated source, scratch,
callback, thread, lifetime, and type resources and leaves the generated
normal and unwind post AST unchanged. The same transformed contract template
is used for the body and callable interface. No runtime signature changes,
ownership or length-arithmetic axioms, MaybeUninit permission, or global
SmallSort/quicksort restriction is introduced.

Call binding checks the exact Freeze clause list, trait method name, and
generic/operand arities in the exact diagnostic caller; the selected impl
bodies are uniquely renamed only after checking their compiler impl clauses.
MIR has no resolved implementation DefId, while the existing generic
specializer may ignore clauses. Therefore the selected branch remains a
conditional source qualification: reaching the clause-ignoring generic route
for a bound call is a hard rejection, and even a successful translation gives
no proof credit for actual unconstrained quicksort dispatch. The independent
two-impl threshold probe remains necessary to establish selected result 32
versus fallback result 16. No whole quicksort, helper, or SmallSort proof is
claimed.

The sole special abort lowering is inside the uniquely named helper body at
the exact zero-substitution, zero-operand `std::intrinsics::abort` call with
no destination and `Unreachable` unwind. It uses the existing
`std::process::abort` contract (req true, ens false, on_unwind_ens false, terminates), whose
false normal and unwind posts preserve divergence. The source's allocation-failure arm
and saved call edge motivate this exact mapping. Every other call and every
other `Unreachable` edge retains existing lowering.

The falsifiable gates are exact extracted source digest; exact four-body and
full unwind inventory; selected impl clause identity; exact caller call
clauses/arity with no generic ignored-clause fallback; preserved normal and
unwind post AST; positive proof of helper entry `ptr_len(v) <= 32`; rejection
of the in-guard `len <= 31` assertion; and rejection of the source-array
leak at the selected method's native source precondition. Until Cloud source
identity, method binding, and all native proof stages are verified, the patch
is unaccepted diagnostic infrastructure only.

## Final static review — unfinished admission gates

The final text has call counters but lacks the final after-translation cardinality
check. This gate remains incomplete; no counter success is claimed. The exact
full caller clauses for T,F/FnMut and erased lifetime substitutions must also be
observed before widening the present strict admission shape. Compilation, full
MIR/AST identities, bound/pointer/unwind/resource controls and runner-oracle
integration are all pending. The candidate is deliberately absent from the
runnable driver/recipe. It cannot receive actual caller or conditional helper
proof credit in its current state.
