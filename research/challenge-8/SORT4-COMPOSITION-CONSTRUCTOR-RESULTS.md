# Composition and runtime constructor phase — closeout

Historical phase below remains CLOSED. Separately authorized
[pointer ownership follow-up](SORT4-POINTER-OWNERSHIP-RESULTS.md) now accepts the
new experimental model/SAFE constructor at O4/37601511894/source182ddf29,
profile325af428/artifact11473086721. Its complete MIR/negative criterion supersedes
the old C8 boundary; actual select reaches as_mut_ptr and stops there. Earlier
UNACCEPTED/NOT AUTHORIZED statements describe the older profile and checkpoint.

2026-10-07. **CLOSED at the authorized ownership boundary.** Entry checkpoint
85d82998e148394e5dbbb0a4ed8c326780130b75; work on challenge-8/research in
Tiramisu-Cake/verify-rust-std. All started Actions completed and full logs/artifacts
were inspected. No active run. New phase consumed **816/5400 summed hosted job
seconds (13m36s), 8 NEW runs**, including setup/build/upload. Remaining4584s
retired; historical closed budgets unchanged. No server builds/verifier/tests.

## Accepted results

**Pure SWO composition:** C1 verifies sort4-swo-composition.c and all11 named
component/application bodies on stock VeriFast26.09,194statements with return/leak
checks. It retains the full index permutation and three adjacent sorted/stable
postconditions for all four distinguishable original occurrences under fixed
strict weak order laws and preserved keys. The checked finite-SWO rank bridge
supplies the universal four-occurrence transfer; this is not the concrete i32/Kani
result. Transitive ranks give global sortedness; equal endpoint ranks force
intermediate ranks equal, and transitive original-ID ordering gives stability.
The equal-key reversal negative fails solely at its intended stability assertion
21,42–44. C1's old classifier incorrectly expected22; C2 reclassifies authentic
saved C1 bytes with complete source/profile/header binding and3 rejection mutants,
without rerunning the verifier. All component files, includes and workflow/runner/
checker wiring were checked. [Audit](SORT4-SWO-COMPOSITION-AUDIT.md).
This accepts pure mathematics; actual Rust expressions, pointer provenance,
callback/value preservation, resources and unwind remain separate obligations.

**Layout control:** C3 runs the unchanged d4a12525 profile's full original stock/
patched6+6,18extra,7metadata,10native paired cases and41span/classifier checks.
All match their expected outcomes. N2's old invalid hi8,col13 is preserved as
history. The repaired mutant changes only binding hi.col.pos13→12, giving
lo(7,0)..hi(7,12) in actual `pub struct Z;` (line7 length13); canonical defSpan
still ends(7,13). Both endpoints are real, ordered/nonempty; every other nested
metadata field and original defSpan is unchanged. Full nested span comparison,
truncated and ambiguous endpoint/field controls fail closed. Export/decode/
encode/refinement/source integrity pass; VF1 solely binding mismatch at7,1–14.
[Repair evidence](SORT4-LAYOUT-CONTROL-REPAIR.md). Patch SHA256 remains
`d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14`.
This adds negative calibration, not an ownership model or automatic UB theorem.

## New experimental patch and trust boundary

[Design](SORT4-MAYBEUNINIT-NEW-DESIGN.md) was committed d67fa0c before semantic
edits. [Patch](verifast-maybeuninit-new-pointer.patch) SHA256:
`cbf7b7dabb6ab50c74688ca5a96ab24e7df0aac8ec3970eaa17f7b255e25a70c`.
It changes **only** src/rust_frontend/vf_mir_translator/vf_mir_translator.ml on
official source809de4596839b739dd999f9e462242c835e3af46. Translator source hashes:
before7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803;
aftere439a7411f0b69cb7a0202c48be5b1bb71d900c5159ef0e178fc79a483cd2009.
C8 built console8f6e78e3b85d8175dba2e90a69e0597bacccdffe6a27e3f8fafc0c854ef47d02.

The narrow rule admits a source-local SAFE free-function adapter specialized at
*const Element, with exact copied runtime body, exact generic union fields and
attached reprtransparent. It maps this one local union to existing opaque
MaybeUninit pointer model, translates its active value aggregate using the
existing value constructor inside the ordinary function body, and redirects the
unchanged external runtime new call to that CHECKED-body candidate. It is not a
runtime call rewritten directly to a ghost fixpoint or a bodyless summary.
Pointer value has no Element:Copy/Freeze bound. Adapter omits unused Copy derive/
manual Clone implementation; this recorded trait-surface difference does not
alter the copied constructor body or repository std/signatures. Fixture enables
transparent_unions, already enabled by core on the same frozen nightly.

New trust links are local union representation/active-field translation and
source equivalence of external call and specialized local copy. Source digests,
exact body/fields/signature/contract bytes, definition/body spans, pointer type,
active field and translation/call counts gate applicability. Exported DefId path
strings alone do not authenticate external-body identity. C8 is deliberately
partial: an exhaustive typed MIR dataflow/no-extra-operation whitelist remains
unimplemented. No general union/alias/memory model, ownership bridge, primitive
copy, FnMut, Drop, schema/exporter/prelude/spec/refinement/kernel or layout change
was made; no historical patch chain used. The profile is **UNACCEPTED**.
Current harness additionally rejects full-acceptance mode before execution;
post-result guard is a static orchestration edit, not new proof evidence.

## Constructor and actual callee

C4 fixed an OCaml shared-record type inference build error. C5 built but found
Rust contract clauses require separate ghost ranges. C6 established intended
stock/patched assertfalse failures but found missing parentheses in fractional
points-to. C7 passed all8baselines and found the omitted transparent_unions crate
feature. Each rerun tested that concrete correction; no identical unexplained
blocker was repeated.

C8 passes all8baselines: stock/patched false assertion at14,16–21, stock/patched
pointer-resource frame39statements/return/leak and four paired native C/C++ cases.
Constructor export/decode/refinement are0 and all source-integrity audits pass.
Certificate admits the exact local body; MIR has one external runtime constructor
call and translator records one redirect, one inner wrapper call, one aggregate.
**First causal failure** is VF1 at verified/lib.rs10,75–102:

~~~text
Function prototype implementation check
No matching heap chunks:
std::mem::MaybeUninit_own(pointer_typeid(Element_typeid))(_t, result0)
~~~

This happens before checking the constructor runtime body: constructor body
header count0 and frameprobe count0. Neither value/provenance preservation,
initialization, frame, nor normal/no-unwind constructor theorem is accepted.
The automatic SAFE-function template requires ownership of the result. Stock
rust_parser.ml1135–1149 creates opaque MaybeUninit_own with no body; lib.rsspec
429–486 supplies only value equations. gen_contract4152–4182 requires result-own;
adding that opaque resource to the explicit post would not derive it from the
actual constructor body. No ordinary proof annotation creates this resource.
No false assertion unexpectedly proved. Source/refinement success is not proof.

Per owner boundary, extension stops before implementing ownership support.
Full MIR gate and constructor wrong-value/false-post/assertfalse/resource and
unsupported-form controls remain **designed / NOT RUN**, not accepted negatives.
The dependent rerun of actual select_unpredictable is **NOT RUN**, because the
constructor was not accepted. Historical N6 actual-callee evidence remains:
stock first call reports missing runtime new; no new statement about a next
intrinsic, guard, Drop or assume_init obligation was established.
[Actual callee](SORT4-SELECT-CALLEE.md).

## Minimal next project — NOT IMPLEMENTED / NOT AUTHORIZED

A future owner decision must review a checked ownership interpretation for
MaybeUninit<*const Element>, linking its initialized active field/model value to
the SAFE template's result-own resource. It must own no Element cell, preserve
full pointer/provenance and independent frame, permit arbitrary Element, and
justify initialization and normal/unwind behavior from the actual body. The
current opaque predicate cannot simply be given an assumed introduction lemma.
No unsafe adapter or deleted safety template is an admissible substitute.

That model/trust proposal needs its own applicability/source/representation
argument and positive/false-result/false-post/assertfalse/duplicated-permission/
unsupported-form gates, stock separation and regressions. Complete the focused
MIR dataflow whitelist before acceptance. Only after checked constructor support
may the unchanged actual callee be repeated; general unions/alias/copy/FnMut/Drop
remain separate decisions. This is a project description, not an extension made
under this phase.

Full sort4 additionally needs a verified actual pointer callee; expression-to-
logical-index/source-pointer bridge; callback value/key preservation under
ordering premises and all five panic/resource posts; actual reference/copy
permissions/provenance/alignment and raw uninitialized scratch ownership; and
caller composition. Existing generic H_align and scalar range geometry remain
accepted independently. ZST logical IDs can share addresses. General safety
retains ZST, non-Copy/non-Freeze, raw scratch and legal callback effects/panics.
RAPx CLOSED/NO-GO, B/C NOT RUN; no other sorting function or external PR/publication.

## Hosted run ledger

| Run | Exact source SHA | Job seconds | Result |
| --- | --- | ---: | --- |
| [C1/37585795831](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37585795831) | 0383012d9a8e5266c6ac34503b6b886fa795882a | 43 | Pure positive PASS; negative classifier mismatch |
| [C2/37586573468](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37586573468) | 4e7ee103a6dbfea7d64a88ebbec62d484eea95cc | 26 | Saved C1 audit PASS; composition accepted |
| [C3/37586921301](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37586921301) | 3844c5fe708f59bab7f5c4b7aff4d6a0de54985d | 179 | Repaired layout/full matrix PASS |
| [C4/37590641832](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37590641832) | ac6dfcf246a72f4e9066041b0e31b810553d117d | 95 | OCaml compile failure |
| [C5/37591112968](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37591112968) | bc72f28cbffe0fb61927c1be2756db430c82e931 | 107 | Built; Rust ghost-range parse failure |
| [C6/37591620888](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37591620888) | 39181a39ffa25b07ad2c47a520bd0bba001a5a5e | 119 | Fractional predicate parse failure |
| [C7/37592046851](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37592046851) | 2e2eaa7d641b05a3109f1c6ac3fe0f5c40cab058 | 122 | Baselines PASS; missing cratefeature |
| [C8/37592506846](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37592506846) | 53b64a780650f6bece661ad751429f628966a63a | 125 | Baselines/gates PASS; opaque own boundary |

Current profile retains compiler db3e99bbab28c6ca778b13222becdea54533d908,
x86_64-unknown-linux-gnu, schema7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9,
exporter2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c,
refiner9f38829f30cb3295653ca111b53592946a97807eee54cba438fffed14c8c1ffe.
Downloaded evidence is outside git, /tmp/sort4-constructor-RUNID.log and
/tmp/sort4-constructor-RUNID-artifacts. Actions artifacts have7-day retention.
Minimal default-main workflow exposure196121c11fee754327692a6aae7c97670d809c74
adds only manual selection/runner/30min cap; research history was not merged.
Completed edits committed/pushed; std runtime and generic signatures unchanged.
Final branch/documentation SHA is reported by the closing commit; tested C8 SHA
above is distinct. Working tree clean after closeout, no active runs.
