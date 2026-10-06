# Challenge 8: C verification research and transfer boundaries

Recorded: 2026-10-06. Scope: preserve the research discussed with the owner.
This is a literature/source review, not an experiment, a new proof result, or a
revision of the project's next phase. [STATUS.md](STATUS.md) remains authoritative.

The inspected project revision is
[`d436977f9dd2bbc8ec4892174df1fd5a2f778dee`](https://github.com/Tiramisu-Cake/verify-rust-std/commit/d436977f9dd2bbc8ec4892174df1fd5a2f778dee).
All references below resolve through the
[artifact catalog](C-VERIFICATION-ARTIFACTS.md), which records immutable source
versions, file paths, evidence classes, and reproduction limitations.
[Sorting model observations](SORTING-MODEL-OBSERVATIONS.md) preserve the separate
finite-enumeration claims from the conversation.

## 1. Findings and their evidence level

SmallSort in this repository is Rust code; the C artifacts are external reference
developments. Its mathematical problems have meaningful C counterparts. Concrete
C developments exist for exchange, insertion sort, and merge. They supply
specification patterns, loop invariants, and list/multiset lemmas. No complete
formal verification of the exact Rust SmallSort composition, or a directly
transferable proof of quadsort's parity merge, was identified in this research.
That is a limited search result, not a claim that no such proof exists.

| Material | What was inspected | What can be claimed here |
| --- | --- | --- |
| ACSL by Example swap, insertion sort, merge | C sources, ACSL contracts, selected predicate definitions, result JSON files and toolchain metadata | The publisher records 10/10, 86/86 and 533/533 discharged obligations respectively; we did not rerun Frama-C |
| VeriFast mergesort example | Annotated C source and lemma bodies, including the version at the project's verifier source pin | A concrete source-level proof development is available; no new VeriFast run or whole-example success claim is made here |
| VMCAI 2019 pointer-analysis paper | Paper, Figure 2, Section 2 and experimental setup | A different pointer-based sort interface illustrates memory partitioning and separation constraints |
| Théry's sorting-network work | Paper and the current pinned `nsort.v` definitions/lemmas | Formal zero-one and permutation theory is available in Coq; it has not been connected to our Rust functions |
| quadsort | README and `parity_merge` C source | Algorithmic provenance and implementation reference, not a located proof certificate |
| Conversation's finite enumerations | Reported counts; Rust schedules and selection expressions inspected again | Historical model observations only; original scripts/logs are unavailable and nothing was rerun |

The source review confirms the published ACSL counts, not the soundness of every
tool/dependency or compatibility with a newly installed toolchain. A green report
for an integer C function is not a generic Rust safety proof.

## 2. Exact Challenge mapping

The pinned [challenge](../../doc/src/challenges/0008-smallsort.md) names seven
safety targets and requires sorting contracts for the three trait methods. It
also requires arbitrary valid slice lengths, the source's safety conditions, and
automatic checking of dangling/misaligned accesses, uninitialized reads,
immutable-byte writes, and invalid values. Helper contracts may be needed.

| Challenge target | Meaningful C formulation | Useful external material | Remaining Rust-specific connection |
| --- | --- | --- | --- |
| `StableSmallSortTypeImpl::small_sort` | Sort a small array, optionally using disjoint working storage | Insertion and merge invariants | Default versus Freeze specialization, scratch initialization, cleanup and ownership; stable behavior needs its own specification |
| `UnstableSmallSortTypeImpl::small_sort` | Dispatch between implementations for different element capabilities | Contracts for the selected components | Prove applicability of each specialization and the fallback/Freeze delegation |
| `UnstableSmallSortFreezeTypeImpl::small_sort` | Select fallback, buffered or network sort using type-size/capability conditions | Component contracts and network theory | Freeze/CopyMarker distinctions, stack-size conditions, complete dispatch coverage |
| `swap_if_less` | Conditional exchange of two valid cells | ACSL swap contract | Branchless pointer selection, overlapping-copy rules, `ManuallyDrop`, callback and unwind effects |
| `insertion_sort_shift_left` | Extend an already sorted prefix by insertion | ACSL insertion sort and rotation lemmas | Arbitrary valid length/offset, `insert_tail`'s logical hole and guard lifecycle |
| `sort4_stable` | Select four input elements into an output buffer in stable order | Pointer-analysis case study; independently derived selection model | Exact five-comparison decision procedure, input/output aliasing obligations, non-Copy ownership and panic paths |
| `has_efficient_in_place_swap` | A predicate comparable to `sizeof(T) <= 8` | Direct source inspection suffices to identify its intended value | Type layout and target architecture; its name is not a performance theorem |

The three trait methods share substantial implementation; they are not three
unrelated sorting algorithms. Conversely, finishing one helper does not establish
any entire trait method.

### Source structure relevant to this mapping

At the pinned revision:

| Entry/component | Source behavior |
| --- | --- |
| Stable default | Calls insertion with offset 1 for length at least 2 |
| Stable Freeze | Calls `small_sort_general_with_scratch` with caller-provided scratch |
| Unstable default | Uses insertion fallback |
| Unstable Freeze delegation | Calls the Freeze trait's selected implementation |
| Freeze default | Chooses general or fallback based on the scratch stack-size condition |
| Freeze + CopyMarker specialization | Also considers the network path using the size heuristic; the marker is documented as an optimization heuristic |
| General path | Presorts blocks of 1, 4 or 8; extends both halves with `insert_tail`; merges back under `CopyOnDrop` |
| Network path | Presorts with the 9/13 networks when applicable, extends by insertion, merges when length is at least 18 |
| `sort8_stable` | Two calls of `sort4_stable`, then `bidirectional_merge` |

Threshold constants are 16 for fallback and 32 for general/network. General
scratch is 48 elements; network scratch is 32; the stack-array budget is 4096
bytes. These dispatch constants do not create a universal `len <= 32`
precondition for the standalone insertion helper.

The helper checks `offset == 0 || offset > len` and aborts on that branch.
On its ordinary sorting path, `1 <= offset <= len`; `offset == len` performs
no insertion. Sortedness of `v[..offset]` is a functional premise, not a
justification for restricting arbitrary-comparator safety. The upstream question
about lengths beyond the thresholds remains a question in the inspected issue
comments, not an accepted exemption. See R3 in the catalog.

## 3. Separate the claims before reusing mathematics

For a fixed, well-behaved order on immutable logical keys, the desired functional
shape is:

```text
Sorted_R(A_after)
Bag(A_after) = Bag(A_before)
```

A bag records multiplicities. A set equality is insufficient: duplicate or lost
elements can leave a set unchanged. For stability, add element identities and
require original relative order for equivalent keys. Sortedness plus bag equality
alone does not establish stability.

Safety must also hold for safe user callbacks that are stateful, return
inconsistent answers, or panic. A nondeterministic Boolean models arbitrary
comparison decisions, but does not by itself model interior mutation, borrow
lifetimes, or unwinding. On unrestricted types, equality with a pre-call
*value* snapshot can be too strong if the callback legitimately changes interior
state. Keep structural element/resource preservation distinct from an immutable
key model used for functional correctness.

The C examples use built-in comparisons on `int`. Their no-callback setting
does not establish the unrestricted Rust `FnMut(&T, &T)` contract. Do not
silently add purity, Copy or Freeze premises to a safety target that lacks them.

## 4. Conditional exchange: ACSL swap

Artifacts A1-A3 contain a plain three-assignment swap and its contract.
The two pointers must be valid; only their cells may change; each final value is
the other's old value. The header does not require the two cells to be separated,
so it should not be paraphrased as a distinct-address-only theorem.

For a mathematical compare-exchange, the normal-result specification is:

```text
if less(b, a): (a_after, b_after) = (b_before, a_before)
else:          (a_after, b_after) = (a_before, b_before)
```

Under a valid order this yields an ordered pair and preserves its bag. With an
arbitrary Boolean decision it still describes either exchange or identity, but
does not imply orderedness.

Actual Rust uses `select_unpredictable` to choose pointers, reads one selected
element into `ManuallyDrop`, then uses `ptr::copy` and
`ptr::copy_nonoverlapping`. The comparator runs before these moves. Therefore a
comparator panic occurs before the algorithm creates that temporary, but this
does not mean callback-induced interior state changes are undone.

Transferable: the small exchange relation, frame condition and multiset lemma.
Unfinished connection: pointer validity/provenance, permitted alias cases,
temporary storage, ownership, and normal/unwind resource restoration for the
actual source. The C proof cannot be substituted for that connection.

## 5. Insertion: prefix induction plus a logical hole

Artifacts A4-A8 specify and implement C insertion sort using
`upper_bound + rotate`, not Rust's backwards pointer-shifting loop. The header
promises sortedness, multiset preservation, termination and no function exit of
the ACSL `exits` kind. Those clauses are not Rust unwind contracts.

The source's loop maintains:

- an index between zero and the array length;
- an ordered processed prefix;
- the same multiplicities within that prefix as at entry;
- an unchanged unprocessed suffix;
- a decreasing remaining-length variant.

The rotation establishes permutation of the affected range and orderedness of
the extended prefix. `Increasing` uses all index pairs; `WeaklyIncreasing`
uses adjacent pairs. Their connection relies on the order's properties.

For Rust's outer insertion loop, the corresponding induction starts at
`offset`, not zero. A proposed mathematical invariant, assuming fixed keys, is:

```text
offset <= i <= n
Sorted_R(A[0..i))
Bag(A[0..i)) = Bag(A_initial[0..i))
A[i..n) = A_initial[i..n)
```

These are candidate specifications, not annotations already verified in this
project. The current bounded insertion evidence remains described by
[insertion-contract.md](insertion-contract.md) and [coverage.md](coverage.md).

### The inner loop needs a different resource invariant

In `insert_tail`, the first comparison happens before `tmp` and the guard
exist. If insertion is needed, the tail is read into `ManuallyDrop`, a
`CopyOnDrop` guard tracks the gap, and cells shift towards the tail.

The mathematical bookkeeping can use:

```text
Bag(original elements)
  = Bag(current array excluding the logical gap) + {temporary element}
```

The gap is a logical ownership hole; it need not contain physically
uninitialized bytes. Stale bytes or temporary copies do not justify owning or
dropping a non-Copy value twice. The memory assertion must connect the logical
sequence to initialized storage, permissions, the guard's destination and one
valid ownership sequence.

At each shift, the old gap is filled and the gap moves left. Normal exit and
late panic require filling it from the temporary. First-comparison false return
and first-comparison panic require their own routes because no guard yet exists.
This is exactly why the C invariant does not resolve the project's current
borrow/recovery blocker. See [INSERTION-RESOURCE-LEDGER.md](INSERTION-RESOURCE-LEDGER.md)
and [BORROW-RECOVERY-DESIGN.md](BORROW-RECOVERY-DESIGN.md).

## 6. Four elements: selection logic and memory are separate obligations

The pinned `sort4_stable` makes five comparisons. It orders two pairs by
selecting input pointers, chooses the minimum/maximum and the two remaining
identities, orders those two, then copies four elements to the output.

It is not the usual five-compare-exchange network. Replacing it with such a
network, or citing a proof of a different `sort4`, would change the verification
target. The exact selection equations, tie behavior, and reported finite checks
are preserved in [the model note](SORTING-MODEL-OBSERVATIONS.md).

Artifact P1 (Bouillaguet et al., VMCAI 2019) uses a different interface with input,
output and permutation-position pointers. Figure 2 abstracts away the sorting
body. Section 2 allows input aliasing but separates inputs from outputs/positions,
and separates output/position locations from one another. The method uses
per-call pointer analysis to simplify the memory model; the paper itself flags
the C record/array reinterpretation as debatable. It is useful methodology,
not a portable drop-in proof of our five-comparison Rust routine.

Potential decomposition:

| Layer | Obligation |
| --- | --- |
| Selection | Selected identities form a permutation for all Boolean decisions |
| Ordered behavior | A consistent order makes selected values sorted |
| Stability | Equivalent keys retain their original identity order |
| Memory | Every read/copy is valid; writes do not clobber later reads; each `copy_nonoverlapping` meets its preconditions |
| Ownership/unwind | Normal copies and callback panics preserve the required resources for the actual caller |

The Rust source's short safety comment states four readable inputs and four
writable outputs. Do not treat that alone as a proved complete aliasing contract.
Any additional separation/ownership requirement must be justified from the
implementation and actual callers, and a genuine missing safety condition must
follow the project's upstream-policy process. This review establishes no new
contract or bug finding.

All five comparisons precede the output copies. This gives a useful panic-path
shape, but does not discharge borrow recovery or authorize ignoring callback
effects.

## 7. Fixed networks: reuse a theorem, then prove the implementation bridge

The actual `sort9_optimal` and `sort13_optimal` contain fixed schedules of 25
and 45 calls to `swap_if_less`. They reference Bert Dobbelaere's catalog (N1).
Their names do not supply a proof of minimality or correctness.

The zero-one principle applies to a fixed network of correct min/max
compare-exchanges over an appropriate order. A threshold map to Booleans commutes
with compare-exchange; an alleged inversion would induce a Boolean inversion.
Consequently, complete Boolean coverage suffices for the abstract network's
sortedness. It does not establish stability or Rust memory safety.

Artifact N2 supplies Coq/SSReflect theory. The inspected `nsort.v` contains
`sorting`, `sorted_sorting`, `sorting_sorted`, `perm_cfun`, and
`perm_nfun`. This offers both an ordering reduction and explicit permutation
reasoning, but the specific Rust schedules still need connection to that theory
and an accepted automated check.

A possible composition is: verify actual compare-exchange; justify that actual
calls realize the fixed schedule; certify that schedule; compose contracts.
This is a research option, not a selected next phase. A rewritten Boolean model
alone cannot replace the first two obligations.

## 8. Merge: strongest C reference, largest implementation gap

### ACSL forward merge

Artifacts A9-A13 require readable sorted inputs, writable output, output
separated from each input, and a non-overflowing total length. The inputs are not
required to be disjoint from each other. Only the output is assigned. The
postconditions state sortedness, union of the input bags, and unchanged inputs.

The loop tracks indices `i, j, x`, with `x = i + j`; its completed output
prefix is ordered, contains the consumed input bags, and is bounded above by
each available next input value. A decreasing sum of remaining lengths supports
termination. A final copy handles the unconsumed suffix.

This is directly useful as a template for consumption counts, boundary order,
framing and bag conservation. The published 533/533 count includes proof support
beyond a single automatic SMT call; the JSON records 13 Coq obligations.

### VeriFast mergesort

Artifact V1 connects concrete C arrays with logical lists using separating
conjunction. `merge_sort_core` receives an input sequence plus separate working
storage; its postcondition returns `sorted(vs)` in the first array and restores
the scratch resource. Recursive calls sort halves, a forward merge builds the
result, and a copy loop moves it back.

The logical `sorted` function is defined using insertion. It is not the
implementation algorithm. The relevant lemmas connect counts, permutations,
sorted lists, and sorting a concatenation after sorting its parts. The catalog
gives their exact names and locations.

The wrapper `merge_sort` requires `n <= 15000`, allocates scratch, aborts on
allocation failure, and frees scratch. The core contract has no explicit 15000
cap, but still operates within valid arrays and machine-representable C inputs.
This is modular symbolic reasoning, not enumeration of every array up to 15000.
It also does not model generic Rust values or Rust panic cleanup.

### Rust bidirectional merge and quadsort

The Rust comment explicitly credits Igor van den Hoven's quadsort and says the
adaptation performs two writes per iteration rather than the original parity
merge's four. Q1-Q2 document quadsort's bidirectional/parity approach and a
concrete C implementation. This establishes lineage, not implementation identity
with every quadsort revision.

Rust consumes from both ends and fills both ends of the destination. Under a
valid fixed order, a candidate invariant is:

```text
The filled output prefix and suffix are each sorted.
Every prefix element <= every remaining element <= every suffix element.
The two filled output regions do not overlap.
Bag(input) = Bag(prefix) + Bag(unconsumed inputs) + Bag(suffix).
The four source frontiers and the two destination frontiers match the counts.
```

Additional obligations include the two half lengths, odd-length leftover,
one-past/temporarily out-of-bounds pointer values, non-aliasing, and completion
of the middle region.

The ordered-input consumption invariant cannot be reused unchanged for
inconsistent comparators. Safety needs bounds independent of the comparison
results. The source can encounter inconsistent frontiers and then panic; its
final check prevents use of the inconsistent destination as a valid result.
Caller cleanup and the ownership of source/scratch remain essential. A theorem
for ordinary forward merge does not prove this behavior.

## 9. Language and tool boundaries

| Boundary | Consequence for reuse |
| --- | --- |
| Rust implementation versus a C translation | A verified translation requires a separate semantics/property-preservation argument before it says anything about the original Rust |
| `wrapping_sub` in `merge_down` | A direct C `p--` can be undefined merely by forming an out-of-array pointer; an integer-index model avoids that C operation but adds a representation connection |
| `MaybeUninit` | Track when storage becomes initialized and when forming/reading a typed value is allowed |
| `ManuallyDrop`, raw reads/copies | Track ownership independently of byte copying; prevent duplicate destruction |
| `CopyOnDrop` and panic | A normal-return C theorem is not an unwind theorem |
| Rust references/provenance | Equal addresses do not automatically carry equal permissions or valid reference lifetimes |
| Type specialization | C integer results do not establish unrestricted generic behavior, zero-sized types or every layout |
| Frame/alias assumptions | Preconditions for a C example must not silently strengthen the Rust target |

Supporting references S1-S6 distinguish tool reuse from language translation.
Kani supports modular contracts; the choice is not “bounded monolithic Kani
versus modular VeriFast”. A verified callee summary still needs the correct
source/domain and usable contracts. VeriFast's Rust documentation explicitly
describes incomplete language support; an attractive proof method is not proof
that the frozen tool profile handles the entire module.

The pinned challenge tool list includes Kani, ESBMC through GOTO-Transcoder, and
VeriFast for Rust. The ESBMC route consumes a Kani-generated GOTO representation,
rather than a handwritten C rewrite. Frama-C/WP is a reference verifier for the
C artifacts here, not an approved replacement Rust pipeline established by this
review. The general rules require approved integrated tools, automation and
unchanged standard-library runtime logic unless an upstream Rust change is
incorporated.

## 10. Preserved questions, not a new roadmap

The earlier discussion suggested “swap → sort4 → insert_tail → bidirectional
merge” as one investigation order. Preserve it as a historical suggestion only:
the repository already contains later experiments and its current phase ended
at a recovery/architecture boundary. This note neither restarts insertion nor
selects sort4, a verifier change, or a new tool.

Questions for the separately requested planning iteration:

1. Which candidate contract can the existing, frozen semantics express for the
   actual source, including callback effects and all unwind routes?
2. Which mathematical lemmas should be independently developed, and how will
   their relationship to memory/ownership be checked?
3. What exact evidence would connect network certificates or selection models
   to actual Rust calls?
4. Which alias/domain assumptions need explicit justification or organizer
   clarification before claiming complete coverage?
5. What is the accepted arbitrary-length scope for each target, especially the
   standalone insertion helper?

No foreign proof code is imported. No runtime source, proof script, verifier
profile, workflow, coverage result, STATUS, or active phase is changed by this
documentation task. Any future execution follows AGENTS and the runbook.

