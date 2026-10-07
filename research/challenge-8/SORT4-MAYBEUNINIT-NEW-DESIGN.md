Current follow-up: [pointer ownership phase](SORT4-POINTER-OWNERSHIP-PHASE.md)
records the separately authorized definition and trust delta BEFORE implementation.
The following design/closeout describes the previous translator-only phase.

# Narrow checked `MaybeUninit::new` route for pointer selection — design only

This is a proposed **separate experimental VeriFast profile**, not an implemented
patch, accepted specification or proof result. The authorized target is the two
actual `MaybeUninit::new` calls in repository `core::hint::select_unpredictable`
at `T = *const Element`, with arbitrary `Element` and no `Element: Copy` bound.
The exact body remains the one checked for source integrity in N6. A successful
constructor component would only let the unchanged callee reach its next
obligation; it would not establish selection, resource transport or sort4.

## Source and first boundary

- Repository `library/core/src/hint.rs` SHA256
  `d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8`,
  blob `fe59166363b9cc049c0d48f4349f4dc9c0e458b8`, contains the two calls
  and full `DropOnPanic`/intrinsic body. N6
  [37549040942](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549040942)
  exported both call sites and stopped at adapter line 21 with `No such function:
  std::mem::MaybeUninit::<T>::new`; no constructor post was checked.
- `library/core/src/mem/maybe_uninit.rs` SHA256
  `7d588bf99e1bd7293b4b9c40fd71a6d5ed71ec6945920b166fc0c90547785702`
  defines `#[repr(transparent)] union MaybeUninit<T>` with `uninit: ()` and
  `value: ManuallyDrop<T>` at lines 340–348. Its actual `const fn new(val: T)`
  at lines 396–398 returns `MaybeUninit { value: ManuallyDrop::new(val) }`.
  The active field is `value`; the argument is moved into it once.
- `ManuallyDrop::new` currently wraps `MaybeDangling::new(value)` in
  `library/core/src/mem/manually_drop.rs` SHA256
  `17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b`;
  `MaybeDangling::new(x)` returns `MaybeDangling(x)` in
  `library/core/src/mem/maybe_dangling.rs` SHA256
  `1cf24b2ec36fff143f329f2ef6db5b4d47cfa798da7f30d88b554b712c8f4b53`.
  The frozen translator already treats `ManuallyDrop::new` as identity for its
  representation (translator lines 2412–2418). That existing wrapper rule is
  a declared trust dependency, not a new permission or `Element: Copy` premise.
- The frozen `lib.rsspec` (lines 429–486) models `MaybeUninit<T>` as an opaque
  struct with `new_maybe_uninit(option<T>)`, ghost `new(v) =
  new_maybe_uninit(some(v))`, `inner`, and optional/initialized points-to
  conversion lemmas. Ghost `MaybeUninit::new` is **not** a registered runtime
  function or a verified body. The opaque `MaybeUninit_own` declaration has no
  definition (`rust_parser.ml` lines 1144–1147); this proposal cannot invent
  ownership transport through it.

The frozen exporter collects local `LocalDefId` bodies only
(`vf_mir_exporter/src/lib.rs` lines 246–255), while the N6 output contains an
external `std::mem::MaybeUninit::<T>::new` call but no constructor body.
`encode_body` also calls `def_id.expect_local()` near line 1303. Direct external
MIR acquisition is therefore not a prerequisite for the proposed route. The
practical narrow route is to compile a **certified source-local constructor
copy** and verify its body, then admit a separate, explicitly reviewed
source-equivalence link from the actual external call to that checked local
body. A local copy by itself has another DefId and is not proof of the external
call. This link is the main trust decision for the new profile.

## Proposed minimum translation, if the feasibility gate passes

1. Extract the exact union fields and `new` source item/body from the pinned
   repository file into a disposable local module in the hosted adapter. The
   module defines a **local** `MaybeUninit<T>` union with the same `uninit: ()`
   and `value: ManuallyDrop<T>` fields and `repr(transparent)`, and a safe free
   function inside that module with the byte-identical constructor body. The
   enclosing module/import, specialized function signature, compiler-only
   lang-item attributes and the source union's `derive(Copy)` trait attribute
   differ, with every difference recorded and checked. The local adapter omits
   `derive(Copy)` because it would require an unrelated local `Clone` impl;
   this constructor only moves one pointer into a fresh value and does not
   copy the union. This local scope can access its own private `value`
   field, so the frozen exporter sees a local function body. Ghost annotations
   may specify the constructor but, after stripping them, must leave the
   documented local Rust adapter byte-identical. Compiler, target, repository
   core hashes, item spans, union field list, body hash and actual N6 external
   call path/signature must all match. A second independent check compares the
   fixture body/field definitions to the extracted repository bytes, not just
   to a hand-maintained expected string.
2. Inspect the local compiler MIR and the unchanged N6 call MIR in the same
   hosted run. The constructor must contain exactly one argument move, the
   existing `ManuallyDrop::new` wrapper, one `AggregateKind::Adt` with
   `UnionKind = local MaybeUninit<*const Element>`, selected field `value` of
   type `ManuallyDrop<*const Element>`, then return of that result. Check exact
   field index/name/type, no read or initialization of `uninit`, no extra
   writes, calls, drops or unwind-producing operations. The N6 calls must
   retain the canonical `std::mem::MaybeUninit::<T>::new` path and substitution
   `T = *const Element` at both sites. Current exporter serializes DefIds only
   as `def_path_str` (near line 1040); the source/MIR/profile certificate is
   an **explicitly trusted applicability link**, not a claim that the string
   encodes an opaque crate hash or that the local DefId equals the external one.
   Reject a toolchain/core identity inconsistent with the pinned repository
   target. The local body must be included, never skipped as specless.
3. In this certified profile, map only the local union type to the existing
   opaque `std::mem::MaybeUninit<*const Element>` representation; do not accept
   arbitrary local unions or aliases. The narrow handling must cover all three
   otherwise rejecting sites: ADT type/name mapping in `translate_adt_ty`
   (near line 786), local union declaration in `decl_mir_adt_kind` (near 204),
   and `Union -> unsupported` in `translate_aggregate` (near 2962). Suppress
   or translate only the certified local declaration and accept **only** its active
   `value` aggregate, translating the existing wrapper-identity result into
   `MaybeUninit::new_maybe_uninit(some(pointer_value))`. The expression is
   inside the verified ordinary constructor function body; it is never a
   substitute for checking that body. This is the scoped
   active-field representation rule allowed for this phase. All other union
   aggregates, fields, type arguments and nonmatching names remain unsupported;
   do not turn generic union construction into an unrestricted feature.
4. Emit a normal VeriFast runtime function declaration/body for the certified
   constructor and verify it under the kernel. Its contract for pointer input
   `p` requires the ordinary thread token and returns the same token plus
   `result == MaybeUninit::new(p)` (or the equivalent exact `inner(result) ==
   some(p)` together with representation equality); its unwind post is `false`.
   The return must preserve the **full modeled pointer value**, including
   provenance, rather than merely an address integer. No `Element` cell is
   read, written, owned or copied. Separate caller fixtures keep an arbitrary
   pointer-access permission and another disjoint resource in the frame and
   prove they remain usable after the call. The function must not produce a new
   `Element` permission or duplicate the original one.
5. Resolve the two **unchanged** external call sites to this checked local
   function body in the shared unit, under the step-1/2 source-equivalence
   certificate and matching type substitution/normal/unwind contract. This
   scoped redirect is a second reviewed trust step; it must be explicit in
   exported evidence and fail closed if the source, call path or body differs.
   A direct call-to-ghost-fixpoint rewrite, an opaque
   prototype with the desired post, or a name-only redirect is forbidden. The
   runtime source and generic signatures stay unchanged. The existing
   `ManuallyDrop` wrapper identity is kept at its pinned rule and source shape;
   if it does not suffice for the concrete pointer instantiation, stop rather
   than adding a second unreviewed wrapper bridge.

This path is a **conditional architecture**, not a claim that the current
translator or kernel can complete it. Newly trusted steps are the narrow local
union type/active-field representation and the exact source-equivalence redirect
from the external core call to the checked local body; neither may be hidden as
a routine function alias. They require the body/field/type/source/MIR certificate
and negative controls. A green proof cannot establish their general soundness.
No prelude, refinement checker, memory model, alignment
patch or historical FnMut/Drop/tuple patch is imported by this design.

## Admissibility and hosted regression gate

Record full hashes of source files, compiler, target, exporter, schema, translator,
prelude/model and this one patch. Keep the constructor and unchanged callee
original/annotated sources byte-equal after removing proof annotations;
preserve export, decode, source integrity, refinement, unwind, leak, validity
and dead-code checks. Use one relevant hosted run at a time within the new
phase's 5400-second total and 1800-second job cap. Before a full callee rerun:

| Gate | Required evidence |
| --- | --- |
| Exact applicability | Pinned repository source/item, local-copy extraction, compiler/target, local MIR and actual external call path/type certificate admits the real pointer constructor twice. A same-name impostor, changed source body, `uninit` field, swapped/wrong argument, nonpointer type, extra union field or unsupported union rejects before proof. Record which check rejects each mutant; do not claim the exported path string alone authenticates DefId. |
| Checked positive body | The certified source-local copy of the actual constructor body verifies once with complete value/provenance equality, token and `on_unwind_ens false`; normal return/leak checks pass. Caller MIR's `unwind: continue` alone is not no-panic evidence. A frame fixture retains independently owned resources while the pointer is wrapped. No unconstrained prototype or assumed summary is used. |
| Intended negatives | With the same valid body and premises, wrong-result-pointer/`inner` post and an executable `assert false` fail at their marked verifier obligations, not setup or the applicability gate. A claimed duplicated permission fails at the ownership assertion. Source-shape mutants are separately expected to fail applicability, not counted as proof negatives. |
| Regression separation | Existing stock index/rank/SWO/network and H_align components retain their original tool/source identities; run representative stock controls separately. Run the constructor profile's positive/negative controls and unrelated Rust/C/C++ regression checks. Do not combine its unaccepted semantics with the exact d4a12525 fieldless layout profile. |
| Actual pointer callee | Only after constructor acceptance, rerun the **same** N6 pointer adapter with all three intrinsics, both guards, `drop_in_place`, `forget`, `assume_init`, exact normal pointer/frame and `on_unwind_ens false` posts. Report the first new causal error. Constructor success alone is not callee success. |

If the asserted falsehood verifies, quarantine this experimental profile and
preserve the reproducer. If the body is skipped, the call resolves through a
ghost function/prototype, or source/refinement/negative checks fail at the wrong
stage, classify the result `INCONCLUSIVE`, not accepted. If the verifier needs
the opaque `MaybeUninit_own` predicate to consume or return ownership, its
current lack of a checked body is the first new ownership-model boundary:
**stop**. A generic union model, permission bridge, raw-copy specification,
callback/Drop support or expanded pointer alias model requires a separate
design/owner decision. The general `sort4_stable` safety domain and all five
panic/resource posts remain open throughout this constructor gate.

## Implementation decision — 2026-10-07, before semantic edits

Within the owner's narrow authorization, root reviewed and selected the
certified-local-body architecture above for an experimental patch over **stock**
VeriFast 26.09. This review occurred before semantic edits. The adapter may
use a **safe free function** specialized at `*const Element`, tentatively named
`sort4_checked_maybeuninit_new`, whose constructor expression/body is copied
byte-for-byte from the pinned repository item; the signature/type path change
from the inherent method is recorded and checked. The local union retains the
two exact generic fields. This avoids requiring general translation of an
associated-function DefKind. The actual external constructor calls still must
resolve to this verified ordinary function under the narrow source/MIR gate.

No unsafe adapter, deletion of generated safety contracts, bodyless prototype,
`MaybeUninit_own` definition or generic ownership bridge may be introduced to
obtain a pass. If the safe function's generated contract requires the opaque
`MaybeUninit_own` transport that cannot be checked, that is the first boundary
and implementation stops there. `Element` remains arbitrary and no `Copy` or
`Freeze` bound is added. Only a new patch artifact under `research/challenge-8`
may contain translator edits; hosted build/verification and its exact runtime
gate are a later step, not part of this design document.

## C4 feasibility gate — deliberately partial

The first hosted run of this patch is a **diagnostic**, not an acceptance run.
It checks pinned source/body and union bytes, local source spans, the typed
pointer constructor interface, active `value` field, one `ManuallyDrop::new`
call, one aggregate, exact external-call count, and ordinary safe-function
body verification against its normal/unwind/resource contract. The frozen
translator still checks all other emitted MIR operations through its ordinary
path. If this run reaches the opaque `MaybeUninit_own` safety template and
cannot prove the body, that is the first ownership-model boundary; stop
without adding an ownership predicate or weakening the generated template.

This partial gate does **not** enumerate and authenticate every MIR operation
and dataflow edge in the local body before applying the representation rule.
In particular, a separate typed MIR whitelist does not yet reject every
possible extra call, write, drop or altered return. Even a green C4 result
therefore leaves the constructor and actual callee **unaccepted**. Before
acceptance, add the focused full MIR shape/dataflow gate described above, run
source-mutant and proof-negative controls at their intended stages, then
check the unchanged callee. The C4 runner must mark feasibility-only mode and
must not dispatch the dependent callee.

## Closeout — C8 ownership boundary

[Final report](SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md). Patch SHAcbf7b7da built;
C8/37592506846/source53b64a7 passed source certificate/export/decode/refinement
and one wrapper/aggregate/redirect diagnostics, then failed the SAFE function
prototype check before runtime body verification at10,75–102 on opaque
MaybeUninit_own(pointer_typeid(Element_typeid))(_t,result0). Body/value/resource/
no-unwind proof NOT ACCEPTED. Stock/patched baselines pass, including intended
false VC. Full MIR gate and constructor acceptance negatives remain NOT RUN;
actual callee NOT RUN. Profile UNACCEPTED. Current checker rejects full acceptance
mode before execution; only the partial diagnostic is implemented.

This activates the designed STOP condition. A next phase would need an explicit
checked ownership interpretation, not a postulated introduction lemma or
unsafe/template-removal workaround. Adding opaque own to the explicit contract
would strengthen the post but would not establish it from the body. The report
records the minimal future project; no bridge/model change is implemented or
newly authorized. Phase CLOSED at816/5400summed jobseconds, no active run.
