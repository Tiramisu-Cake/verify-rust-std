# H_align: concrete Rust ZST versus the pinned VeriFast model

Current phase separately authorized from e170656: stock generic baseline PASS in
run37540829027, then an experimental layout prototype limited further to truly
source-fieldless nongeneric Sized Rust structs. [Phase/matrix](SORT4-ALIGNMENT-PHASE.md#stock-generic-and-fieldless-layout-prototype--2026-10-07)
and [current results](SORT4-ALIGNMENT-RESULTS.md#stock-generic-baseline-and-experimental-fieldless-layout--2026-10-07)
record execution. The audit/review below remain historical: their broader proposal
including fielded structs is NOT the new implementation scope. No fielded exact
layout, offsets/ownership/aliasing or old verifier patch chain is authorized.


The audit and hosted results below are a historical record of the bounded
no-patch phase. The review appended after that record was prepared from
checkpoint b523959 on 2026-10-07. It proposes a future review/implementation
scope only: no VeriFast patch, new axiom, tool build, or patch-regression
verification is authorized or included here. Generic hosted runs are recorded
separately in the results; they do not test a layout patch.

Read-only audit during the 2026-10-07 bounded no-patch phase, checkpoint f1c0774.
Pinned source809de4596839b739dd999f9e462242c835e3af46; no tool patch or execution
accompanies this audit. Hosted results and concrete proof progress are recorded
separately in [results](SORT4-ALIGNMENT-RESULTS.md).

## Source-to-model path

The original type stays `#[repr(align(8))] pub struct Z;`, with Rust size0 and
alignment8. Those are properties to calibrate in the model, not new proof premises.

| Stage | Pinned implementation / saved evidence | Consequence |
| --- | --- | --- |
| Rust fixture | Original/verified sources of37532204465, concrete Z cases | Empty original type with explicit alignment8; no replacement type or annotation layout assumption |
| Exporter | [lib.rs:1100](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_exporter/src/lib.rs#L1100) serializes adt_def.repr().c() | repr alignment8 is not exported as an ADT layout fact |
| Wire schema | [vf_mir.capnp:269](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir/vf_mir.capnp#L269), AdtDef ends with isReprC | No size/alignment or repr(align) field; saved decoded Z has empty fields/isReprC=false |
| Translator | [vf_mir_translator.ml:6043](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L6043) | Reconstructs VF StructType from fields; attaches only ReprC here, not alignment8 |
| Size/alignment expressions | [verifast1.ml:6465](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast1.ml#L6465) | Struct sizeof and alignof are symbolic functions of typeid |
| Struct size assumption | [verifast1.ml:6508](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast1.ml#L6508), unconditionally generated _size_limits | 0 < sizeof(Z) <= max_uintptr; fieldless nonpacked struct gains no equation size0 |

The positive-size fact is incompatible with the actual empty Rust type. The
observed failure at `assert size == 0` in37532204465 and37535499783 therefore has a concrete
model cause. `align==8` was not reached, but the missing exporter/schema/translator
fact already explains why it cannot be inherited from the original repr attribute.
No claim of a new hosted misalignment miss or a std runtime bug follows.

## Why pointer limits fail

[prelude_core.rsspec:189](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/prelude_core.rsspec#L189)
defines typed pointer add through byte add of i * size_of(T), preserving provenance.
The concrete fixture supplies a zero-count array_<u8>; array__inv exposes limits
at base and base+0. It does not promise an additional positive-sized range.
Because the concrete model's size(Z) is positive/symbolic, i>0 can move beyond
that range. This explains the failed pointer_within_limits(ptr_add_(base,i,Z_type_info))
obligation at both37532204465 and37535499783 .add line21. This is a source-model
explanation; the logs alone do not prove one failure causally implies the other.
Actual Rust ZST arithmetic would have zero
stride; no numerical address rewrite or added typed resource is justified here.

Existing is_valid_layout_size_of_align_of and size_align provide nonnegative size,
positive power-of-two alignment and divisibility. They do not derive this exact
struct's size0/align8; deriving size0 consistently would contradict _size_limits.
A checked lemma cannot repair the missing representation fact against that axiom.
Assuming size0/align8, changing Z, manipulating repr/model attributes, or accepting
an inconsistent proof context is outside this no-patch phase.

## Scope of the boundary

The concrete ZST layout/add control cannot be closed faithfully under the present
model and unchanged contract. A future decision would need a reviewed correction
to Rust layout encoding and the struct-size model, with admissibility/regressions,
or another separately justified independent component. No extension is implemented.
Do not add layout assumptions to the adopted caller contract or exclude ZST.

This does not refute independent generic arithmetic geometry. Symbolic generic
size0 remains in that theorem's input domain. Its checked local hypotheses must
come from the original byte/provenance/valid-layout resources. Even a generic pass
cannot silently instantiate a faithful concrete-Z model that the tool lacks, prove
automatic copy UB detection, or close ownership/reference/unwind requirements.
The strict header/assertion replay controls are another independent diagnostic.
RAPx remains CLOSED / NO-GO and B/C NOT RUN.

Latest hosted continuation37535499783/sourceea635ea completed in38s,1/3 NEW slots.
Checked generic helpers/local bounds and i=1,2,3 branch posts/leak checks pass; the
residual generic alignment post remains INCONCLUSIVE. Classifier replay and both
intended negative controls pass separately. Phase CLOSED at this concrete boundary;
unused slots retired, no patch or additional run. The recommended next decision is
a minimum-scope trust/admissibility review of faithful Rust layout encoding versus
an independent component. No proof from an inconsistent size context is acceptable.

## Follow-up layout-model review (documentation only, 2026-10-07)

### Upstream and release check

Read-only snapshot:2026-10-06T22:01UTC (2026-10-07 local checkpoint).
The26.09.20 entry below records identity/date only; the rules were compared at
26.09 and26.10/master.26.10 uses nightly2026-09-25; it was inspected, not run or
adopted as the hosted proof profile.

This review checked the official release records and fetched source tags without
building or running VeriFast. The live `master` ref and official `26.10` tag both
resolve to `f76012fb518703b1d98e243ac4f487f16877cfcb`; release date:
2026-10-05. The adopted `26.09` release/tag is
`809de4596839b739dd999f9e462242c835e3af46`, published 2026-09-06. The intervening
`26.09.20` tag is `7343304bb50c22123747f5e985104365768294ea`, published
2026-09-20. These dates and identities come from the
[official 26.09 release](https://github.com/verifast/verifast/releases/tag/26.09),
[26.09.20 release](https://github.com/verifast/verifast/releases/tag/26.09.20),
and [26.10 release](https://github.com/verifast/verifast/releases/tag/26.10).

The 26.10 source confirms the pinned model boundary remains present:

| Layer | 26.10 source | Observed behavior |
| --- | --- | --- |
| Rust exporter | [lib.rs:1100](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_exporter/src/lib.rs#L1100) | ADT export sets `is_repr_c`; no size or ABI alignment is serialized here. |
| Cap’n Proto schema | [vf_mir.capnp:269](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir/vf_mir.capnp#L269) | `AdtDef` ends with `isReprC`; there is no Rust `repr(align)`, size, or alignment field. |
| Rust translator | [vf_mir_translator.ml:6265](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L6265) | Builds `Ast.Struct` from translated fields and attaches only `ReprC`. It filters `PhantomData` fields; therefore an empty translated field list alone does not prove the source ADT had no fields. |
| Size/alignment model | [verifast1.ml:6465](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/verifast1.ml#L6465), [6497](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/verifast1.ml#L6497) | Struct `sizeof` and `alignof` remain symbolic functions of type identity. |
| Struct-size bound | [verifast1.ml:6519](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/verifast1.ml#L6519) | The engine still assumes `0 < sizeof(struct) <= max_uintptr` without a Rust-dialect guard. |

The corresponding rules are present in the pinned 26.09 source at exporter
`lib.rs:1100`, schema `vf_mir.capnp:269`, translator
`vf_mir_translator.ml:6060`, symbolic `alignof_core` at `verifast1.ml:6486`, and
the same positive-size assumption at `verifast1.ml:6508`. Thus the 26.10 check
confirms persistence across the actual release boundary; it does not change the
profile or results of the hosted 26.09 runs.

### Recommended route: compiler-backed facts for a bounded Rust struct subset

Recommend a minimal Rust-layout representation repair, subject to a separate
trust/admissibility review before implementation. The first implementation scope
should transport the compiler-computed `(size, ABI alignment)` for **closed,
concrete, sized Rust structs with non-generic ADT definitions** using
`repr(Rust)` or `repr(C)`, with optional
`repr(align(N))`. Include fieldless types such as the unchanged
`#[repr(align(8))] struct Z;` and ordinary nonempty structs. Bind each fact to the
source ADT identity, its closed type identity, and compilation target/layout
configuration (initial target x86_64-unknown-linux-gnu). A closed instantiation
of a generic ADT is not included merely because its arguments are concrete:
that needs a per-instantiation wire/typeid design beyond this first ADT-definition
carrier. For Z, the facts must reach the same type identity used by the
engine's `sizeof` and `alignof` expressions and establish exactly size `0` and
alignment `8`.

The minimum proposed code surface is the pinned Rust MIR exporter
[`src/rust_frontend/vf_mir_exporter/src/lib.rs`](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_exporter/src/lib.rs),
wire definition
[`src/rust_frontend/vf_mir/vf_mir.capnp`](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir/vf_mir.capnp),
generated Cap’n Proto bindings regenerated with that schema, the Rust AST
representation in
[`src/frontend/ast.ml`](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/frontend/ast.ml),
the MIR translator
[`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml),
and engine rules in
[`src/verifast1.ml`](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast1.ml).
The precise AST carrier is a design choice for that review. It must not conflate
Rust layout metadata with C/C++ `ReprC`, and generated bindings must match the
schema revision.

The wire carrier should be an explicitly tagged optional layout record, not two
unsigned fields whose default zero is mistaken for a known zero-sized layout.
It carries size and **ABI** alignment, representation/support kind, and a binding
to compiler/target/source/ADT identity. Presence, positive power-of-two alignment,
size divisibility/address-width bounds and identity must be checked; preferred
alignment is not interchangeable with ABI alignment. Unsupported/missing exact
facts remain absent, not fabricated zeroes. The translator must use original ADT
field metadata, never infer source fieldlessness after PhantomData filtering.

The size lower bound should become dialect-aware: retain the current positive
lower bound for non-Rust struct frontends, and use a nonnegative bound for Rust
structs, including Rust repr(C) structs: repr(C) does not change the source
language to C/C++. That Rust-scoped change is needed for generic Rust structs and structs
whose fields are all zero-sized, even when no closed exact-layout fact is
available. Exact compiler-backed facts for the supported closed structs then
constrain their size and ABI alignment. Preserve and audit the engine's existing
field-offset and padding constraints against those exact facts; do not invent or
silently rewrite field offsets to make a layout assertion pass. A missing optional
closed-layout fact must not invalidate unrelated proofs that only use abstract
layout; when a proof asks for an exact fact the model cannot supply, it must
remain unproved or report that layout as unsupported.

Changing only `sizeof > 0` to `sizeof >= 0` is insufficient. It permits zero but
does not entail it: the symbolic size may still be any nonnegative value. It says
nothing about symbolic `alignof`, so it cannot derive `alignof(Z) == 8`, field
offsets, or exact padding. Nor does it by itself prove that `.add(i)` has zero
stride. Layout attributes alone are not a substitute for the compiler's exact
layout result.

Keep generic function parameter `T` symbolic under the existing
`is_valid_layout_size_of_align_of` / `size_align` reasoning. Do not export a
sampled constant layout for a generic ADT and reuse it at all type arguments.
The bounded first repair can leave exact layouts for generic ADTs abstract when
the compiler facts are not closed. A later parametric/per-instantiation layout
design requires its own support analysis. This review does not propose new
support for enums, unions, DSTs, `repr(packed)`, transparent layout, niche
optimization, field permissions, or ABI transport beyond the stated struct
subset.

The trust boundary is material: compiler layout-query results, exporter
serialization, schema decoding, translation/type-identity linkage, and the
engine's generated layout facts become part of the trusted semantics. The
implementation must pin/check target configuration and source/type identity,
reconcile exact facts with existing offset rules, and document unsupported
forms. No new axiom or change to that trusted boundary is implemented in this
phase.

Required trusted premises for that future change are explicit: the pinned rustc
layout query describes the same runtime Ty and target as exported MIR/size_of/add;
serialization/decoding preserve the tuple and its absence state; nominal/typeid
mapping attaches it to that same Ty; and engine-generated facts are compatible
with its existing valid-layout, offset and field rules. These are reviewed tool
semantics, not stronger sort4 caller preconditions or handwritten per-Z axioms.
A consistency regression is required but does not itself prove model soundness.
Any needed offset-rule change beyond importing size/ABIalign is a new review
boundary; report it before broadening the proposed implementation.

### Independent-component alternative and recommendation

Candidate profile: Kani0.67.0, source152c6a8c875d9886a67e229247b4826d6105ccfd,
nightly2026-02-05, x86_64-unknown-linux-gnu; existing evidence and instrumentation
limits are in [the Kani results](SORT4-RESULTS.md#frozen-profile-and-cost) and
[the no-patch assessment](SORT4-NO-PATCH-ASSESSMENT.md). No new Kani run here.

Kani is a plausible concrete calibration component: a harness over the same
ghost-free source revision and pinned target could check `size_of::<Z>() == 0`,
`align_of::<Z>() == 8`, and the zero-stride address property for the relevant
`.add` indices. Require byte-identical extraction of original Z and each
relevant ghost-free geometry body from the tested fixture SHA519a3707136d2ae4e589c44b837afac6c58b939b;
if claiming actual-sort4 applicability, also freeze the repository std blob
e555fce440872898e47fd5114f32eb15401d07df and audit its source/destination offsets.
A rewritten stand-alone numeric function is insufficient. Existing Kani sort4
runs used concrete `i32` and `repr(C)` record
types; there is no recorded Kani Z run in this evidence set. A new Kani Z harness
would therefore be new evidence, not a result already available here.

That component has no type quantification over arbitrary Rust `T`; a concrete Z
run cannot discharge the generic theorem. Nor is there a proven interface that
composes Kani's concrete layout result with the remaining VeriFast proof while
keeping the concrete Z case out of VeriFast's incompatible positive-size model
and preserving the original all-types contract. Its geometry input would have to
quantify every admitted i and original aligned/live base provenance, not only one
allocated sample. A concrete witness buffer is a stricter subdomain, and numeric
address identity supplies no ownership or reference-validity conclusion.

A prospective split must keep Z calibration entirely outside VF compilation units
that generate the incompatible concrete Z axiom. Any VF arithmetic/resource component
would have to remain independently proved over abstract layout parameters without
that concrete declaration, followed by a checked interpretation/interface and an
exhaustive input-domain split. All other ZSTs (including destructor-bearing types)
stay in the target contract. No such all-types split or permission/ownership interface
is proved; injecting Kani's0/8 facts into a VF unit asserting size(Z)>0 is forbidden.
A split theorem or numeric fact
transfer alone would not supply the missing ownership, provenance, or permission
bridge. The independent-component route is therefore a concrete regression
option, not an evidenced replacement for the layout repair or a full-domain
proof. Prefer the bounded compiler-backed Rust layout repair for review.

### Future regression design (not implemented or run)

Future implementation baseline for this minimum proposal is
809de4596839b739dd999f9e462242c835e3af46 /26.09/nightly2026-02-05, preserving the
current evidence profile. Rebase/profile upgrades require explicit review; the
live26.10 comparison does not authorize one. No such implementation is made here.

The following checks are design criteria only. No patch tests, builds, or
verification runs were performed for this review.

| Gate | Required positive/control result |
| --- | --- |
| Original Z layout | With the exact original `#[repr(align(8))] struct Z;`, establish compiler/model agreement on size `0`, ABI alignment `8`, and `.add(i)` address preservation for every admitted `i` in `0..=3`, for both const and mut geometry cases. |
| Ordinary closed structs | Check nonempty Rust structs with multiple fields and padding; compare transported size, ABI alignment, and field offsets to the pinned compiler layout for the same target and closed type identity. Include supported `repr(Rust)`, `repr(C)`, and optional `repr(align(N))` forms. |
| Generic code | Retain a proof over symbolic `T` with valid-layout premises that permit size zero; exercise the generic function at Z and a nonzero-sized type. If generic ADTs remain unsupported for exact facts, two distinct instantiations must not receive one sampled constant layout. |
| Other languages | Preserve existing C and C++ positive-size behavior and representative field-offset proofs; include a C++ empty complete object whose size remains nonzero. Confirm the Rust-only lower-bound rule does not alter these frontends. |
| False layout controls | Deliberately assert wrong Z size, wrong Z alignment, and a nonzero Z stride. Each must fail at its named layout/geometry assertion. Also require `assert false` under normal premises to fail, guarding against a proof accepted only through inconsistent assumptions. |
| Metadata integrity | Missing, malformed, wrong-target, or mismatched-source/typeid layout metadata must fail closed or leave exact layout goals unproved; it must never be silently associated with another ADT/type identity. |

Acceptance requires whole-unit exit0 for positives, body/marked-operation reachability,
all normal/unwind/leak/dead-code/refinement checks active, and negatives failing
only at their intended assertions. A parse/setup/dead-code failure or an unrelated
proof blocker is INCONCLUSIVE for the intended negative. `assert false` must fail
under ordinary satisfiable premises, including the original Z layout proof's
req true; successful posts in an inconsistent normal context cannot pass the gate.
Run the existing relevant Rust/C/C++ proof regressions once the future patch is
reviewed; any Rust proof formerly relying on blanket struct positivity must be
reassessed and derive it from valid concrete facts or nonzero-field premises,
never restore the false universal bound merely to retain green counts.

The checks should compare compiler-produced and transported facts independently
of the assertion being proved, retain the unchanged source type and `.add`
operations, and record exact tool/source/target identities. These regression
cases are not authorization to add assumptions to the sort4 contract.

### Expected scope and remaining sort4 obligations

The next implementation proposal is limited to the five named source layers plus
synchronized generated bindings and isolated hosted regressions, based on the
26.09 pin. First establish an unchanged-tool generic baseline satisfying the
whole-unit dead-code gate; then audit/implement only Rust layout metadata, shared
size/ABIalign facts and the dialect-scoped lower bound. Acceptance is the full
positive/negative/typeid/generic/language matrix above with all checks active.
No historical verifier patch chain, callable-copy summary, alias model or callback
specification is part of this proposal. No implementation starts in this phase.

The recommended bounded repair addresses faithful size/alignment for the
supported closed Rust structs, removes the contradictory positive-size fact for
Rust structs, and makes the concrete Z zero-stride geometry expressible. It does
not establish that VeriFast automatically detects copy UB, prove the whole
`sort4_stable` body, or close ownership/aliasing, comparator effects, unwind,
`FnMut`, `Drop`, or five-call recovery obligations. It does not justify the
historical insertion/FnMut/Drop verifier patch chain; those changes need a
separate source-level and trust-boundary rationale. RAPx remains CLOSED / NO-GO;
B/C remain NOT RUN.

The separately authorized generic follow-up used two NEW runs37537448952 and
37537868053,85s total jobs. The residual zero-index/alignment/resource posts now
discharge, but the unchanged dead-code gate rejects impossible guard assertions:
generic whole-unit status remains INCONCLUSIVE, no accepted theorem. Layout review
is complete and all future patch regressions remain DESIGN ONLY / NOT RUN.

Before a future layout patch regression claims completed generic coverage, the
unchanged-tool baseline must close the whole-unit dead-code gate. A separately
authorized candidate can move finite-index equalities to their reachable proof
cases rather than place assertions in impossible guard bodies, keeping the same
checked index derivation and all target assertions/resources/posts. This is a
proof-structure task, not a solver/layout patch; no such candidate is implemented
or run after this phase's2/2 limit.
