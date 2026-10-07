# `sort4_stable`: memory-operation obligations

This note separates the scalar geometry of the checked range
lemma from obligations carried by Rust references, pointer intrinsics and
ownership. It uses the pinned VeriFast 26.09 source at
`809de4596839b739dd999f9e462242c835e3af46` (repository profile/run evidence in
`STATUS.md` and `SORT4-ALIGNMENT-RESULTS.md`). It does not claim that any
operation-level diagnostic has run under VeriFast.

## Exact operations and specifications

In `library/core/src/slice/sort/shared/smallsort.rs`, `sort4_stable` forms ten
shared references by `&*v_base.add(...)` for comparator arguments (lines
626,627,641,642,649), then selects four source pointers and calls
`ptr::copy_nonoverlapping(..., dst.add(k), 1)` for `k = 0,1,2,3` (lines
653–656). Selection and alignment facts alone do not establish a valid shared
reference, readable/writable ownership, or a copy postcondition.

The pinned `bin/rust/std/lib.rsspec:545–550` contract for
`copy_nonoverlapping<T>` requires a readable initialized typed source range
`[?f]src[..count] |-> ?vs` and an already initialized typed destination range
`dst[..count] |-> _`. It preserves the source fraction and replaces the
destination value with `vs`; it has no unwind path. Thus it directly does not
model `sort4_stable`'s potentially uninitialized `MaybeUninit<T>` scratch
destination. The byte-oriented `copy<T>` contract at lines 514–543 does not
bridge this gap: in its non-overlap branch it permits optional source bytes
`|-?->`, but still requires initialized destination bytes `|-> _`; its post
only returns optional bytes. It is not a typed validity, padding ownership, or
initialized-to-raw-scratch contract. The `MaybeUninit` model around lines
429–487 represents the inner value as `option<T>`; this distinguishes an
uninitialized slot from `some(T)` but does not change either copy contract.

`prelude_core.rsspec` defines `points_to` as initialized `points_to_` at lines
212–213 and typed arrays in lines233–247. The array split/join lemmas at lines
260–283 preserve same-typed ranges and their fractions.
Conversions between byte ranges and typed ranges are separate: in particular
`u8s__to_array_<T>` (line335) explicitly requires
`p as usize % align_of::<T>() == 0`; `from_u8s_<T>` at line 327 has the same
alignment precondition. `write_bytes<T>` at `std/lib.rsspec:551–554` also
states an explicit typed alignment condition. These clauses matter when those
conversion/write lemmas are used; they do not imply that the body of
`copy_nonoverlapping` runs an alignment check.

## Reference creation and alignment coverage

The MIR translator's `Rvalue::Ref` handler in
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` (around lines
3007–3110) may erase reference construction for mutable borrows or immutable
places marked `place_does_not_need_drop`; otherwise ordinary shared references
map to `create_ref`/`reborrow_ref`, with unwind wrapping when enabled. For the
sort comparator's shared `&T` arguments, whether the path is materialized
depends on the exported MIR flags and the exact `T` instantiation. The
`aliasing.rsspec` contracts for these calls (lines 77–98) carry
`ref_precreated_token`, `ref_init_perm`, `ref_initialized`, pointer equality,
and `ref_origin` facts, but no arithmetic alignment clause is visible in these
contracts. This is a source/model observation, not evidence that a reached
verification accepted a misaligned reference or that the frontend misses a
runtime obligation. The Rvalue path must be confirmed in an actual hosted
fixture before making that coverage claim.

No clean negative reference fixture is currently justified. A misaligned
`&*p` must not obtain a typed `T` resource by assumption: that assumes the
validity under test. Conversely, without that resource the failure may occur
at fixture setup rather than at reference construction. A useful future
negative needs a sound raw-byte allocation/ownership setup and a checked
reference-creation boundary whose target assertion is specifically alignment;
the inspected opaque aliasing predicates alone do not supply that setup.

Similarly, a manual assertion that `addr % align_of::<T>() == 0` is a proof
of the arithmetic assertion, not an automatic detection test for UB in
`&T` formation or a copy intrinsic. The prior RAPx ZST-misalignment
`SOUND_MISS` is a separate verifier/profile result and does not test this
VeriFast operation path. Existing VeriFast H_align assertions establish
geometric facts only. The typed byte-to-array lemmas show that some typed
conversions demand alignment, but neither proves reference validity nor
measures intrinsic enforcement.

## ZST and scratch boundary

For ZST, `size_of::<T>() == 0`: distinct logical source indices remain distinct
occurrences, while their pointer addresses may be identical and byte ranges
are empty. Empty ranges do not establish value ownership, a valid `&T`, or the
non-null/alignment requirements of typed references and pointer operations.
The fieldless-only layout profile is now fully accepted at
[run 37547890530](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37547890530),
source SHA `3f5c9e3126a6db0599f1b989f03146e143342d04`, with the required exact
experimental patch. That accepts this bounded layout prototype only; it does
not establish generic layout for all `T`, actual copy/reference enforcement,
or any pointer/resource bridge. Stock generic H_align results likewise do
not establish actual copy/reference enforcement.

The current copy specifications leave one precise design gap: a checked
operation interface must consume initialized source ownership and writable
raw destination ownership for the exact byte/typed span, preserve source
resources as required by the caller, and return an explicit optional/raw
destination representation that composes with `MaybeUninit<T>`. Its contract
must account for validity and padding without manufacturing initialized `T`
resources or duplicating ownership. A separate ownership bridge must explain
how a copied representation becomes the caller's single eventual owner.
Design and review that interface plus positive/negative primitive controls
before considering any trusted specification change; no trusted change is
made here. The actual `copy_nonoverlapping` body/callee remains unproved.

## Checked scalar range lemma and experiment card

`sort4-range-lemmas.c` states a pure integer theorem and composes it with the
shared `sort4-index.gh` theorem. Given mathematical
offsets `s,d`, nonnegative `stride`, source/destination full half-open spans
`[s,s+4*stride)` and `[d,d+4*stride)` that are ordered and disjoint, and
logical indices `i,j` in `0..3`, each unit slot interval lies inside its full
span and the two unit intervals are ordered/disjoint. The composition lemma
calls the index theorem and maps the exact `min`, `lo`, `hi`, `max` expressions
to destination slots 0,1,2,3. Its source-index inputs are therefore derived
from the actual logical selection formulas without comparator consistency
premises. The proof uses the frozen prelude multiplication-monotonicity lemma for
index and endpoint bounds; it introduces no new arithmetic axiom.
At `stride == 0`, these are
empty ranges even when bases coincide; no distinct-address conclusion follows.
The lemma says nothing about machine overflow, pointer provenance/allocation,
alignment, initialization, alias permissions, source-code selection, or
operation execution. It can become a premise for selected indices only after
the independent index theorem and an actual pointer/resource bridge are
established.

Before its first hosted check:

- **Hypothesis:** pinned VeriFast 26.09 checks the scalar range lemmas and
  their selected-index composition using its
  ordinary arithmetic reasoning, without added assumptions or model changes.
- **Exact domain and posts:** arbitrary mathematical offsets; `stride >= 0`;
  `0 <= i,j <= 3`; ordered disjoint full spans. Posts establish only cell
  containment and scalar cell-separation. The composition case links exactly
  the selected `min/lo/hi/max` indices to dst slots 0,1,2,3 and returns the
  index permutation fact. It has no runtime call, so no normal/unwind effect
  or resource post is claimed.
- **Profile:** stock pinned profile, hosted Actions only; source/contract
  integrity and ordinary leak/dead-code checks retained. Rust refinement is
  inapplicable to a ghost-only C theorem; no Rust adapter bridge claimed.
- **Expected positive:** the range and exact `min/lo/hi/max` composition lemmas
  reach their complete postconditions.
  A frontend/setup/arithmetic-proof failure is inconclusive, not an operation
  UB result.
- **Minimal negative marker:** a separate scalar mutant keeps the valid
  `stride > 0` and ordered-span premises, then claims the final cell's endpoint
  `d + (3+2)*stride` lies within `d + 4*stride`. The expected failure is its
  named target assertion only. If an earlier setup or unrelated arithmetic
  assertion fails, the negative is invalid.
- **Next step:** if positive, use this only as scalar range evidence; decide
  separately whether existing typed split/resource lemmas bridge selected
  locations. If that bridge or raw-scratch summary is missing, document the
  minimum primitive/ownership design and do not add a trusted implementation.

Hosted acceptance N8/37549955948,source9b25c410f6f69bdf5649aabf98481501824cec1e:
stock VF0,24 verified statements, all four named helper/composition bodies and leak
checks complete; negative rejects only marked endpoint line10. N7's earlier integer
case residual is retained as failure evidence; identical domain/posts pass after
using existing multiplication monotonicity. No operation-level UB test was run.
