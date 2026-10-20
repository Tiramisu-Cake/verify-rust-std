# R11 P0c observer cleanup: checked-route design and applicability boundary

## Finding

R10's bounded P0c observation identifies a resource leak in the generated
diagnostic body `a1_guard_observer` at `verified/lib.rs:139`: the verifier still
owns `Option_own(...)(_t, left_ancestor_pivot)` when the body returns. This is a
generated-observer proof failure, not evidence that the actual stable quicksort
has a runtime heap leak.

The fixture builder's `_observer` in `a1-fixtures.py` (around lines 245–259)
keeps the actual quicksort signature and guard prefix and appends the diagnostic
assertions and early return. The parameter is the actual, arbitrary
`mut left_ancestor_pivot: Option<&T>` from
`library/core/src/slice/sort/stable/quicksort.rs`. Before the generated return,
the prefix has not reached the later assignment `left_ancestor_pivot = None`
at source line 72. Neither the source nor the current proof establishes that the
parameter is `None`; both `None` and `Some(&T)` remain in scope.

## Pinned source audit and checked cleanup routes

The pinned VeriFast tool commit is present in `/root/verifast/.git` as Git
object `f76012fb518703b1d98e243ac4f487f16877cfcb`; its tree is
`d7e55e183ecabfdb0a79cfe600fd0f2419124926` (parent
`5ae8339482dea6ce3b382c58736560a635194277`). I read these immutable Git
objects directly; I did not build, run, or edit that checkout. Relevant paths
and exact Git blob IDs at this commit are:

| Path at pinned commit | Git blob |
| --- | --- |
| `src/rust_frontend/vf_mir_translator/rust_parser.ml` | `e27eee316f6ba809ca6fe2111e42f217745e45bf` |
| `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` | `4e237a61a7e4449735e53220114e57114b51e31a` |
| `bin/rust/std/lib.rsspec` | `a5d925d67c7934105a7a95c532c84edee8f3afd4` |
| `bin/rust/rust_belt/general.rsspec` | `6c60c0e942b441901741889309858185a5572ebe` |
| `bin/rust/aliasing.rsspec` | `e9864ee0f618681a334d54c54a76b94fc438b912` |

`rust_parser.ml:995–1015` synthesizes enum ownership from the constructor
fields: its `SwitchExpr` gives `None` an empty assertion and `Some(x)` the
field's `<FieldType>.own(t, x)`. Thus `Option<&'a T>.own(t, None)` is empty;
`Option<&'a T>.own(t, Some(r))` contains `<&'a T>.own(t, r)`. The exact Rust
std declaration is at `std/lib.rsspec:1500–1505`; `std/lib.rsspec:414–417`
defines `drop<T>` with precondition `thread_token(?t) &*& <T>.own(t, value)`
and normal/unwind postcondition `thread_token(t)`. This supplies an existing
checked way to consume either a whole `Option_own` or, after variant-aware
opening, a `Some` payload's `&T` own chunk.

For shared references, `vf_mir_translator.ml:1558–1630` maps the shared `&T`
ownership interpretation to the pointee's share predicate. The generic
`shared_ref_own` constructor is defined as `[_]pointee_shr` in
`rust_belt/general.rsspec:66–68`; `close_ref_own` at lines 194–196 goes from
that persistent pointee share to `<&'a T>.own`. The pinned tree search found
no separate `open_ref_own` or discard lemma. Semantically, opening
`Option_own` exposes `<&'a T>.own`, which the existing generic `drop` contract
can consume. That transition itself needs no axiom or assumption and covers
both variants; however, current parser/checker syntax cannot express this
generic open without a concrete lifetime/type argument. The exact applicability
failure is recorded below.

The explicit whole-value call remains the first and smallest Cloud hypothesis:
`core::mem::drop(left_ancestor_pivot)` immediately before each observer exit.
It preserves the original arbitrary parameter and relies directly on the
existing `drop<Option<&T>>` contract. If Cloud shows the original
`Option_own` remained in S1. The variant-aware form was then rejected by the
static applicability audit below; do not send the attempted annotation to
Cloud.

`Option<&T>` is Rust `Copy`, so Rust semantics leave a source local usable after
a by-value use. The pinned translator source does not establish how that
availability maps to this ghost resource: `vf_mir_translator.ml:2242–2256`
notes that MIR `Copy` and `Move` are represented separately, while
`:2281–2286` erases both to the same AST operand expression. An explicit
function call is a MIR `Call` and is translated through `translate_fn_call`;
an implicit MIR `Drop` terminator is separately translated to
`std::ptr::drop_in_place` at `:2916–2950`. This is source-level evidence for
the checked-call route, not proof of actual Copy lowering or that rustc retains
this explicit call in the Cloud pipeline. Cloud remains the falsifiable check.

The historical R10 profile pins selected-base `lib.rsspec` SHA
`d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf` and
`library/core/src/mem/mod.rs` SHA
`b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`.
Finding the pinned tool source in Git objects corrects the earlier statement
that the source commit was unavailable in this worktree. R11's final effective
`proof_std`/overlay reconstruction against this object is still not established
by this static audit.

## S1 Cloud falsification

The S1 Cloud attempt `ec83aeb7-b15f-4bde-a95d-ccf7e1b58100` falsified the
whole-value `drop` candidate: the source-reported caller still exits with
`Option_own(...)(_t, left_ancestor_pivot)` at `verified/lib.rs:141`, after the
two observer `drop` calls. The paired Evidence Brief reader artifacts are
`P0c-error-lines.json` (1925–1936) and source `source-cleanup` lines 130–141;
file ID `edc4344315735b949d8cc08c7b2987a02755370189b812d0b03a29e1b2dffd15`,
SHA-256 `4873a15c2b0bbae576815acae69fb6e3c9f0fe7be1daa8cce5f0c8a39289893c`,
source ID `4d40abec9cab7cafa2f552ebd1b7d42d4b7f7479707033e4a1e9a057b211415c`,
SHA-256 `c6b726448036d4a3d1f356bbd262de389664affec6931210986f5e08a5e0aa1d`.
The source-bound paired normal MIR reader record is file ID
`420a134958a20e7bba13f2c5ecf96a725bdd64bcc470bd84bcb9202f455a4422`,
SHA-256 `3a53b6fb8dc3a5765582dd609a685720bb7880595ff31fa74111134c568132d1`;
the supplied source/MIR locates place the observer at line 8084 and retained
`mem::drop` calls at 9662, 10096, and 12574. These records show the explicit
calls were present while the Option predicate still remained at the caller
exit. This is a proof failure in the diagnostic body, not a runtime leak.

## Pinned checker applicability finding

The proposed next candidate was variant-aware: open the generated
`Option_own`, match its value, and consume `Some(r)` with the existing
`drop(r)` contract. Source inspection rules out the two syntax shortcuts that
would avoid spelling the elided borrow lifetime. In the pinned
`rust_parser.ml:515–533`, a type-predicate open on a constructed type forwards
its type arguments as written. `Option_own(_t, value)` therefore has an empty
type-argument list. In `verifast.ml:1400–1406`, the generated enum predicate is
resolved as `PredCtorInfo`; the checker zips its generic parameters with those
arguments and raises “Incorrect number of type arguments” when they are
omitted. The earlier predicate-family branch (`verifast.ml:1364–1375`) does
support inferred arguments, but generated enum ownership is a predicate
constructor, not a predicate family.

The annotation `<std::option::Option<&'_ T>>.own(...)` also cannot infer the
input's elided borrow lifetime. `rust_parser.ml:41–108` requires a literal
lifetime token after `&` and turns `'_` into the identifier `"'_"`.
`verifast1.ml:2069–2138` resolves that identifier as a named type parameter or
declared type; it does not bind it to the Rust local's inferred region. `T` in
the generic source signature may likewise not be a ghost type parameter
visible by that name at the inserted source location. This is a static
applicability failure, not a semantic objection to opening the enum predicate.

That rules out direct variant-aware `open` syntax with omitted type arguments
and the literal `'_` annotation. A checked generic lemma provides a separate,
source-bound route without changing the observer signature:

```rust
lem a1_cleanup_option_ref<'a, T>(value: std::option::Option<&'a T>)
    req thread_token(?t) &*& std::option::Option_own::<&'a T>(t, value);
    ens thread_token(t);
{
    open std::option::Option_own::<&'a T>(t, value);
    match value {
        std::option::Option::None => {}
        std::option::Option::Some(r) => {}
    }
}
```

This helper uses explicit, in-scope `'a` and `T` in its own checked contract and
body, while the ghost call at the observer supplies only
`left_ancestor_pivot`. Unlike `open`, ordinary generic function calls infer
omitted type arguments: `verifast1.ml:5066–5069` creates an `InferredType` for
each callee parameter, and Rust mode enables strict type-parameter matching
(`verifast1.ml:92`, `:3280–3306`). Strict unification recursively matches
constructed `Option` arguments and `RustRefType` lifetimes/type arguments, so
the call can bind the helper's lifetime from the local's actual translated
region.

The Some arm intentionally performs no raw-reference open or runtime drop.
`vf_mir_translator.ml:1624` maps shared-reference `.own` to the pointee's
`.share` assertion. The generic ADT `.share` builder at `:829–840` wraps that
share in `CoefAsn(DummyPat, ...)`; `rustbelt.ml:9–14` describes this as
duplicable share permission. Thus unfolding the generated Option predicate
and selecting `Some(r)` leaves only a dummy-coefficient share, which the
existing leak checker treats as leakable. `None` contributes `Emp` by
`rust_parser.ml:995–1015`. The helper's only non-persistent resource is the
thread token, which its postcondition returns. This is a checked disposal of
the local predicate; it introduces no axiom, assumption, `leak`, `forget`, or
runtime std change. The helper does not call `share_full_borrow`,
`init_ref_share`, or another operation whose contract requires
`type_interp<T>`; its precondition is exactly the existing `thread_token` and
`Option_own` resources.

The static route is viable but not yet proof evidence. Cloud must check the
exact generic lemma declaration/call syntax, lifetime inference, Option enum
pattern checking, and that the Some-arm residual is recognized as leakable in
the selected effective specs. The S1 direct-drop fixture remains falsified;
the generated candidate now calls this lemma instead. If any obligation fails,
P0c remains open with zero proof credit. No hard-coded compiler region name is
used.

The project proof source illustrates both the positive construction and the
missing end condition. In
`verifast-proofs/alloc/collections/linked_list.rs/verified/linked_list.rs:2798–2801`,
`Iter::next` obtains reference share permission, calls `close_ref_own`, then
closes `Option_own(Some(elem_ref))` to return the option. It returns the
reference permission rather than discarding it. Its `end_ref_Option_NonNull`
lemma at lines 632–645 requires `ref_initialized`, an
`ref_end_token_Option_NonNull`, and a fractional points-to chunk for the
referenced Option place; on `Some`, it invokes `std::option::end_ref_Option_Some`
and `std::ptr::end_ref_NonNull`. Those place/token resources are not established
for the by-value `left_ancestor_pivot` local. Applying this lemma by analogy
would be unsound until its exact precondition is proved from the active caller
and lifetime.

Assigning `None` is a separate falsifiable lowering candidate, not an assumed
cleanup: it must consume the old arbitrary variant's resource exactly once and
must not synthesize an end-of-lifetime token for a still-live caller reference.
Matching the value establishes which field exists but likewise does not consume
that field. For `Some(&T)`, any `end_ref` use must prove the exact borrow
origin, lifetime-dead/end token, and restoration behavior; merely opening or
dropping the field cannot stand in for those facts.

## Decision and controls

The direct whole-value drop was tested and left `Option_own` at the generated
observer return. The current candidate replaces that call with the checked
generic ghost lemma above, called at both observer exits and the labeled P1
tail. It retains arbitrary `None` and `Some(&T)` inputs. This is a falsifiable
Cloud candidate, not an accepted proof; failure leaves P0c open with proof
credit zero and does not establish a runtime leak.

The R10 `a1-tool.py` reconstruction statically checks the selected baseline's
`critical`, `effective_rsspec`, `proof_std`, and modified-file maps before
building, and checks that effective spec/source identity is unchanged after
each overlay (around lines 290–301 and 459–485). The pinned tool source commit
is available as the Git object listed above; this does not by itself establish
R11's final effective maps. Do not widen scope to alter the active model or
runtime std to make the diagnostic pass.

The fixture injects the generic lemma in a ghost block and replaces each
whole-value runtime drop call with a ghost lemma call. Synthetic tests check the
lemma's generic contract, both `Option` arms, absence of trust-changing
constructs, observer signature/guard prefix retention, and P1 tail placement.
They establish generation only; Cloud must verify the checked body, inferred
lifetime, and required posts. No proof credit or profile acceptance follows
from static/synthetic results. The controls must preserve arbitrary inputs and
reject:

- `None`-only behavior masquerading as the general observer proof;
- a `Some(&T)` path that leaks or duplicates the reference ownership;
- cleanup that consumes the caller's unrelated resources or changes the
  comparator/guard obligations;
- missing or altered Option/ref `own` or `drop` contract, wrong owner, or
  unsupported lowering, without treating setup failure as an intended
  negative.

Static review establishes the syntax-level applicability blocker and the
`Copy` concern only. It provides no verifier result, exact-pair receipt, proof
credit, or acceptance of the experimental profile.
