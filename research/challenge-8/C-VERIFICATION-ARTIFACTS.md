# Challenge 8: external artifact catalog

Recorded and source-checked: 2026-10-06.
Read with [the survey](C-VERIFICATION-SURVEY.md) and
[the historical model record](SORTING-MODEL-OBSERVATIONS.md).
This catalog preserves references and findings; it changes no experiment phase.

## Reading the evidence labels

- **Source inspected:** the relevant text/contract was read, without executing it.
- **Published result inspected:** the author's checked-in result data was read;
  no local or hosted reproduction was performed for this review.
- **Supporting path located:** existence was checked in the pinned repository
  tree; the entire artifact/proof dependency was not audited.
- **Paper inspected:** relevant sections were read; not an independently replayed
  machine-checkable result.
- **Historical observation:** a prior conversation claim without retained run
  provenance. See the model record; never count it as a new proof.

Commit pins identify the snapshot actually consulted here. They do not claim to
be the original research authors' first version or the exact versions used by
the earlier conversation. Public documentation URLs without a commit/version are
explicitly living references, accessed on the date above.

## Authority and separation precedents

Checked on 2026-10-06 for the owner's decision to adopt an explicit
[sort4 domain](SORT4-CONTRACT.md#adopted-domain-and-caller-obligations).
Publication status and inspectable contracts support the assessment below;
we do not infer authority from repository popularity or invent citation rankings.

| Reference | Verified provenance and status | Relevant contract and weight |
| --- | --- | --- |
| P1, Bouillaguet, Bobot, Sighireanu and Yakobowski | [Springer chapter](https://doi.org/10.1007/978-3-030-11245-5_8), VMCAI 2019, LNCS 11388, pp.160–182. The [publisher's proceedings description](https://link.springer.com/book/10.1007/978-3-030-11245-5) explicitly confirms peer review (27 papers selected from 62 submissions). The [official conference program](https://popl19.sigplan.org/details/VMCAI-2019/1/Exploiting-Pointer-Analysis-in-Memory-Models-for-Deductive-Verification) confirms authors and venue. | Strong, directly relevant scholarly precedent. The inspected author version, Section 2/Figure 2, states input/output separation and per-call checking. This is a VMCAI paper, not a POPL main-track paper or merely an unidentified preprint. |
| A, ACSL by Example | Institutional report and reference collection from Fraunhofer FOKUS: pinned [README](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/README.md) and [copyright/license](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/LICENSE.md). README identifies version33.0.1, the accompanying report and Frama-C/WP artifacts. | Credible, inspectable specification precedent. A10 explicitly separates each input range from output; inputs need not be mutually separated. A11's 533/533 goals are published result data, not our reproduction. No peer-reviewed-publication claim for this exact snapshot. |
| V1, VeriFast C mergesort | Pinned example in the verifier's own [source repository](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/examples/mergesort_and_binarysearch.c#L265-L267). | Supporting tool artifact: the two full array resources in `merge_sort_core` are joined by separating conjunction. No separate peer-review or execution claim for this file. |

P1 technical inspection uses the [versioned author text](https://arxiv.org/html/1811.12515v1);
publisher/conference metadata establishes publication status, not a line-by-line
identity audit of the final chapter. Its input pointers may alias each other;
inputs are separated from outputs/positions, whose locations are pairwise
separate. That interface and schematic sorting body differ from Rust sort4.
The paper also flags its record/array reinterpretation as debatable under C.

**Assessment:** these sources are sufficiently authoritative to support choosing
and defending an explicit separated-buffer specification. The argument is
contractual and implementation-specific: state the premise, prove the body under
it, and establish it at calls. A2's swap permits coincident pointers, so these
works do not establish a blanket C rule excluding aliases. The Rust justification
also depends on our actual-body diagnostics and caller audit; neither scholarly
publication nor institutional provenance proves Rust ownership, panic safety,
the weakest admissible precondition, or committee acceptance. No C proof was
replayed and no foreign proof code was imported for this decision.

## Repository snapshots

| Repository/material | Snapshot used | Version purpose |
| --- | --- | --- |
| `Tiramisu-Cake/verify-rust-std` | `d436977f9dd2bbc8ec4892174df1fd5a2f778dee` | Actual target, challenge/rules, current project checkpoint |
| `fraunhoferfokus/acsl-by-example` | `3e8cd9adf79955d9b722185f9beb4518c66d57f2` | Version 33.0.1 per README; all A references use this snapshot |
| `verifast/verifast` | `809de4596839b739dd999f9e462242c835e3af46` | Existing project verifier source pin; C example is already present |
| `verifast/verifast` observed head | `f76012fb518703b1d98e243ac4f487f16877cfcb` | Cross-check only: the example's Git blob is identical to the project-pin copy |
| `scandum/quadsort` | `4c357224cd9b53382248affc64e295726697bd35` | README and C implementation reference |
| `thery/mathcomp-extra` | `e52a2cc7542059484adc6d0902161a56a961704e` | Current concrete Coq source accompanying the network research; not asserted to be the 2022 paper's exact commit |

SmallSort target Git blob: `e555fce440872898e47fd5114f32eb15401d07df`.
VeriFast C example Git blob at both inspected commits:
`78924ff8c4827612d072f9607a104a2422a9c499`.
Coq `nsort.v` Git blob: `c21eaf253da8129b3c6a356059a75eb602e3c102`.

## R — target, rules and organizer discussion

| ID | Artifact | Content/evidence and limit |
| --- | --- | --- |
| R1 | [Challenge 8](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/doc/src/challenges/0008-smallsort.md) | Source inspected: seven safety targets, three sorting contracts, arbitrary valid lengths, required UB checks |
| R2 | [Actual SmallSort source](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/library/core/src/slice/sort/shared/smallsort.rs) | Source inspected: dispatch, thresholds, swap, networks, insertion, sort4, merge and size heuristic |
| R3 | [Tracking issue #56](https://github.com/model-checking/verify-rust-std/issues/56) | Issue comments read on 2026-10-06; discussion is not a replacement for the challenge/rules |
| R4 | [General rules](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/doc/src/general-rules.md) | Source inspected: target is the repository's library; approved integrated tools, automation, runtime-change policy |
| R5 | [Approved tools snapshot](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/doc/src/tools.md) | Source inspected: includes Kani, GOTO-Transcoder/ESBMC and VeriFast for Rust; does not list Frama-C as an integrated Rust verifier |

Exact issue comment anchors:

- [Contributor questions, 2025-01-09; edited 2025-01-24](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2580563254):
  comparator safety versus correctness, value/permutation concerns, reported solver
  cost and a safety-comment question. These are another contributor's reports,
  not our measurements; the comment's informal “invalid values” example should
  not be used as the Rust Reference definition of validity.
- [qinheping response, 2025-01-24](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906):
  other tools welcome; primitive types/default ordering considered substantive
  solutions despite the ultimate arbitrary-type/order goal. This is not a
  blanket waiver of all generic safety, tool-integration or completeness duties.
- [CI runtime guidance, 2025-01-24](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2613110847):
  approximately two minutes per proof is described as an ideal, with discussion
  of Kani/CBMC performance limitations. Do not rewrite this as a strict universal
  timeout or a promise that expensive proofs will be accepted.
- [Open scope questions, 2026-09-05](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-5551156885):
  asks about threshold-length i32 coverage and standalone insertion beyond those
  thresholds (alongside eligibility questions). No response resolving those
  length questions appeared in the comments fetched for this review.

## A — Fraunhofer FOKUS, ACSL by Example

### Code, contracts and reported results

| ID | Exact artifact | What to inspect / evidence status |
| --- | --- | --- |
| A0 | [README](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/README.md) and [typedefs.h](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/typedefs.h) | Source inspected: version 33.0.1; `value_type = int`, `size_type = unsigned int`; not generic Rust types |
| A1 | [swap.c](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Mutating/swap.c) | Source inspected: ordinary three-assignment exchange |
| A2 | [swap.h](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Mutating/swap.h) | Source inspected: valid pointers, assigns two cells, old-value exchange, termination; no separation requirement between p and q |
| A3 | [swap.json](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Results/swap.json) | Published result inspected: 10 proved / 10 total |
| A4 | [insertion_sort.c](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Sorting/insertion_sort.c) | Source inspected: prefix invariant, upper_bound, rotate, frame and decreasing variant |
| A5 | [insertion_sort.h](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Sorting/insertion_sort.h) | Source inspected: valid array, sortedness and multiset preservation |
| A6 | [insertion_sort.json](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Results/insertion_sort.json) | Published result inspected: 86/86, including 13 in the Coq field |
| A7 | [upper_bound.c](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/BinarySearch/upper_bound.c), [upper_bound.h](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/BinarySearch/upper_bound.h) | Supporting paths located; called by A4; not independently rerun or fully audited |
| A8 | [rotate.c](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Mutating/rotate.c), [rotate.h](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Mutating/rotate.h), [RotateLemmas.acsl](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Logic/RotateLemmas.acsl) | rotate paths located; lemma declarations inspected, notably `RotateOne_MultisetReorder` and `RotateOne_StrictLowerBound` |
| A9 | [merge.c](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Sorting/merge.c) | Source inspected: forward merge, consumption indices, bounds, bag invariant and tail copy |
| A10 | [merge.h](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Sorting/merge.h) | Source inspected: sorted inputs, separated output, length bound, sorted multiset union and unchanged inputs |
| A11 | [merge.json](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Results/merge.json) | Published result inspected: 533/533, including 13 in the Coq field |
| A12 | [MultisetReorder.acsl](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Logic/MultisetReorder.acsl), [MultisetUnion.acsl](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Logic/MultisetUnion.acsl), [Increasing.acsl](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Logic/Increasing.acsl), [WeaklyIncreasing.acsl](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Logic/WeaklyIncreasing.acsl) | Definitions inspected: value counts across states, union of counts, all-pairs versus adjacent ordering |
| A13 | [Interactive proof directory](https://github.com/fraunhoferfokus/acsl-by-example/tree/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Session/interactive) | Supporting paths located; contains Coq proof files, not replayed here |
| A14 | [ACSL by Example report](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/ACSL-by-Example.pdf) | Supporting report path located and identified by README; no new full-PDF audit claimed |

Useful located proof dependencies in A13:

- [lemma_RotateOne_MultisetReorder.v](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Session/interactive/lemma_RotateOne_MultisetReorder.v)
- [lemma_MultisetReorder_DisjointUnion.v](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Session/interactive/lemma_MultisetReorder_DisjointUnion.v)
- [lemma_MultisetReorder_Shift.v](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Session/interactive/lemma_MultisetReorder_Shift.v)
- [lemma_MultisetUnion_Reorder.v](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Session/interactive/lemma_MultisetUnion_Reorder.v)
- [lemma_MultisetUnion_TailLeft.v](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Session/interactive/lemma_MultisetUnion_TailLeft.v)

These are navigation aids, not a complete dependency closure for any one result.
No declaration is promoted to a proved imported axiom in our project.

### Result fields retained from the publisher's JSON

| Example | Proved | Total | Qed | Alt-Ergo | CVC5 | Z3 | Coq | term | unreach |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| swap | 10 | 10 | 5 | 3 | 0 | 0 | 0 | 1 | 1 |
| insertion_sort | 86 | 86 | 27 | 44 | 1 | 1 | 13 | 0 | 0 |
| merge | 533 | 533 | 347 | 162 | 10 | 1 | 13 | 0 | 0 |

These are artifact fields, not timings, our run statistics, or a new aggregate
proof count. Preserve the publisher's categories rather than calling every goal
“automatically solved by SMT”.

### Reproduction metadata

[toolchain.json](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Results/toolchain.json) and README
were inspected. The recorded toolchain is Frama-C 33.0 Arsenic, Why3 1.8.2,
Alt-Ergo 2.6.3, CVC5 1.3.4, Z3 5.1.0 and Coq 8.20.1.

The snapshot's [Makefile](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Makefile),
[configuration guide](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Config/README.md) and
[verification configuration](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/StandardAlgorithms/Config/verify-local.mk)
are located setup references, not commands validated in this project.
Replaying a result requires the source, imported logic, interactive sessions,
machine model, configuration and compatible provers; the JSON alone is not a
standalone proof certificate.

[License](https://github.com/fraunhoferfokus/acsl-by-example/blob/3e8cd9adf79955d9b722185f9beb4518c66d57f2/LICENSE.md): MIT, inspected. This commit links to the material
and explains the mathematics; it vendors no source/proof implementation. Any
future code reuse would need attribution/license review as well as compliance
with the project's independent-proof policy.

## V — VeriFast C mergesort and list lemmas

**V1:** [examples/mergesort_and_binarysearch.c](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/examples/mergesort_and_binarysearch.c).
Source and lemma bodies inspected. The same file at
[the observed head](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/examples/mergesort_and_binarysearch.c)
has the identical blob recorded above. This cross-check is not a tool upgrade.

| Symbol | Role in the development |
| --- | --- |
| `is_sorted_between` | Ordered list with lower and upper bounds |
| `insert_sorted`, `sorted` | Mathematical insertion and canonical sorted list |
| `count_eq`, `same_count`, `is_permutation` | Multiplicity-based permutation definition |
| `count_insert_sorted`, `count_sorted` | Count preservation through mathematical insertion/sorting |
| `is_permutation_sorted` | Connects counts to the permutation predicate |
| `insert_sorted_commut`, `insert_sorted_append_cons` | Reordering/insertion algebra used to relate concatenations |
| `sorted_append_flip`, `sorted_append_insert_sorted` | Concatenation and insertion rearrangements |
| `sorted_sorted`, `sorted_append_sorted` | Idempotence and sorting already sorted halves |
| `insert_sorted_is_sorted`, `sorted_is_sorted` | Connect canonical sorting with the ordering predicate |
| `is_sorted_weaken`, `is_sorted_limits`, `is_sorted_sorted` | Bound and orderedness support |
| `sorted_append_is_sorted`, `is_sorted_insert_sorted` | Reasoning about merging sorted remainders |
| `merge_sort_core` | Array-to-list contract, recursive halves, forward merge, copy-back |
| `merge_sort` | Scratch allocation/free wrapper with `n <= 15000` |

The example imports `arrays.gh`, `quantifiers.gh` and `target.gh`.
Its internal merge uses loop requires/ensures over the remaining array segments,
not merely the same prefix invariant as the ACSL implementation.
Binary-search lemmas later in the file are outside the SmallSort transfer scope.
No command line, verifier execution, success log or dependency soundness audit
was produced for V1 in this review.

## P — pointer-heavy C sort case study

**P1:** Quentin Bouillaguet, François Bobot, Mihaela Sighireanu and Boris
Yakobowski, *Exploiting Pointer Analysis in Memory Models for Deductive
Verification*, VMCAI 2019.
[Published chapter, DOI 10.1007/978-3-030-11245-5_8](https://doi.org/10.1007/978-3-030-11245-5_8);
[Versioned record](https://arxiv.org/abs/1811.12515v1);
[PDF](https://arxiv.org/pdf/1811.12515).

Paper inspected: Figure 2 and Section 2 describe `sort4` using an input/output/
position-pointer struct; the sorting body is schematic. Section 6 discusses
Frama-C Eva/WP experiments for several sizes and calling contexts. Use this for
memory partitioning and permutation-interface ideas. It is not the Rust
five-comparison algorithm, a generic Rust proof, or a standalone downloaded
verification package. No external executable artifact was reproduced here.

## N — sorting-network catalog and formal theory

**N1:** Bert Dobbelaere,
[Smallest and fastest sorting networks](https://bertdobbelaere.github.io/sorting_networks.html).
Living catalog accessed 2026-10-06; the Rust source references it. Entries
[9 inputs / 25 comparators](https://bertdobbelaere.github.io/sorting_networks.html#N9L25D7)
and [13 inputs / 45 comparators](https://bertdobbelaere.github.io/sorting_networks.html#N13L45D10)
provide relevant schedules. The exact target schedules are preserved from pinned
Rust in the model note, so reproducibility does not depend on the live page.
Catalog optimality remarks are not proof claims about our Rust implementations.

**N2:** Laurent Théry, *A Formalisation of Algorithms for Sorting Network*, 2022.
[Versioned paper](https://arxiv.org/abs/2203.01579v1);
[HTML](https://arxiv.org/html/2203.01579v1).
The paper presents Coq/SSReflect network theory and the zero-one principle.

Concrete source: [nsort.v](https://github.com/thery/mathcomp-extra/blob/e52a2cc7542059484adc6d0902161a56a961704e/nsort.v) (inspected), especially
`sorting`, `sorted_sorting`, `sorting_sorted`, `perm_cfun` and
`perm_nfun`. The companion paths [more_tuple.v](https://github.com/thery/mathcomp-extra/blob/e52a2cc7542059484adc6d0902161a56a961704e/more_tuple.v),
[bitonic.v](https://github.com/thery/mathcomp-extra/blob/e52a2cc7542059484adc6d0902161a56a961704e/bitonic.v), [bjsort.v](https://github.com/thery/mathcomp-extra/blob/e52a2cc7542059484adc6d0902161a56a961704e/bjsort.v) and
[batcher.v](https://github.com/thery/mathcomp-extra/blob/e52a2cc7542059484adc6d0902161a56a961704e/batcher.v) were located but not replayed or fully audited.
This theory supports a possible reduction; it does not already certify the
Rust 9/13 schedules or establish stability and memory safety.

## Q — algorithm provenance, not a located formal proof

**Q1:** [quadsort README](https://github.com/scandum/quadsort/blob/4c357224cd9b53382248affc64e295726697bd35/README.md), “Parity merge” and
“Branchless parity merge” sections. Source inspected: bidirectional consumption
and optimized merging rationale.

**Q2:** [src/quadsort.c](https://github.com/scandum/quadsort/blob/4c357224cd9b53382248affc64e295726697bd35/src/quadsort.c), `FUNC(parity_merge)`.
Source inspected. [src/quadsort.h](https://github.com/scandum/quadsort/blob/4c357224cd9b53382248affc64e295726697bd35/src/quadsort.h) is a located companion.
Compare to R2's `bidirectional_merge` comment and implementation; do not assert
literal identity. No formal proof of this exact quadsort/parity implementation
was located in the preceding research. The repository's benchmarking material
is not verification evidence.

## S — language semantics and tool context

| ID | Reference | Use and limitation |
| --- | --- | --- |
| S1 | [Rust Reference: undefined behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) | Living semantic guidance, inspected; validity, alignment, references and aliasing must be addressed in Rust, not inferred from a C integer theorem |
| S2 | [Rust pointer wrapping_sub](https://doc.rust-lang.org/std/primitive.pointer.html#method.wrapping_sub) and [WG14 C99 issue 0221](https://www.open-std.org/jtc1/sc22/wg14/issues/c99/issue0221.html) | Language-reference pointers for formation versus dereference and C pointer arithmetic; they do not supply a Rust-to-C translation proof |
| S3 | [Kani contracts](https://model-checking.github.io/kani/reference/experimental/contracts.html) and [project Kani guide](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/doc/src/tools/kani.md) | `proof_for_contract` and `stub_verified` support checked summaries; general modular capability, not evidence that a specific SmallSort contract scales |
| S4 | [GOTO-Transcoder/ESBMC integration](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/doc/src/tools/goto-transcoder.md) and [CBMC](https://www.cprover.org/cbmc/) | Reusing verification backends through a Rust frontend/intermediate representation differs from rewriting the algorithm in C |
| S5 | [project VeriFast guide](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d436977f9dd2bbc8ec4892174df1fd5a2f778dee/doc/src/tools/verifast.md) and [VeriFast Rust Reference](https://verifast.github.io/verifast/rust-reference/) | Separation-logic contracts, memory resources and modular reasoning; Rust language support is incomplete and configuration-dependent |
| S6 | [Frama-C/WP](https://www.frama-c.com/fc-plugins/wp.html) | Deductive checking of ACSL contracts for C; a source of proof patterns, not established approval for a new Rust pipeline |

R1 additionally links a historical Rust Reference revision
[`142b2ed77d33f37a9973772bd95e6144ed9dce43`](https://github.com/rust-lang/reference/blob/142b2ed77d33f37a9973772bd95e6144ed9dce43/src/behavior-considered-undefined.md).
That is the challenge's historical link; its full content was not re-audited in
this documentation pass. Distinguish it from the living Reference above.

## Preservation and execution boundary

This record contains persistent URLs, exact consulted Git revisions, selected
result fields, symbol maps, source-to-target relationships and uncertainty.
Third-party PDFs, source trees and proof code are not vendored. No verifier,
compiler, model test or hosted workflow was executed for this review.

To revisit a source, start from its pin and exact file rather than a search
snippet or the repository's moving default branch. Any future proof replay or
Rust adaptation is a separate experiment under [AGENTS.md](../../AGENTS.md),
[STATUS.md](STATUS.md) and the [runbook](AGENT-RUNBOOK.md).
