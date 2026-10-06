# Pure logical index component for sort4

Prepared under [night authorization](SORT4-NIGHT-PHASE.md); **NOT RUN** initially.
Stock VeriFast26.09 checks owned ghost bodies in [sort4-index.gh](sort4-index.gh)
and [application](sort4-index-lemmas.c), with an isolated
[duplicated-hi negative](sort4-index-negative.c). No imported sorting proof.

For arbitrary independent Boolean replies c1..c5, `s4_index_permutation` requires
true and establishes both intermediate and final permutations. `s4_perm` includes
all four bounds0..3, six pairwise inequalities and exactly-one counts of each
original ID0..3. No comparator consistency, purity, totality or order is assumed.
Five checked Boolean splits exhaust all32 possibilities; no finite value sampling.

The source is `library/core/src/slice/sort/shared/smallsort.rs`, blob
`e555fce440872898e47fd5114f32eb15401d07df`. `s4_a/b/c/d` transcribe Boolean casts
at628–631; `s4_min/max/left/right` transcribe the exact nested condition-selected
expressions at643–646; `s4_lo/hi` transcribe650–651. Copies653–656 use
min,lo,hi,max at destination offsets0,1,2,3. Hosted source-binding evidence records
the exact expressions, ghost right-hand sides and source lines; changed source
or formula fails the binding gate. Boolean-to-usize gives0/1, its negation gives1/0.

`s4_select` is a mathematical conditional fixpoint, **not a summary of the actual
Rust callee**. Neither source-expression audit nor C ghost checking proves
core::hint::select_unpredictable, Rust pointer offset provenance/permissions,
reference formation, copies, initialization, ownership or any panic/resource post.
Applying this theorem to the Rust caller still needs actual callee and pointer
resource bridges at the same source/profile. Independently accepted H_align gives
offset geometry, not these missing bridges. Four distinct logical ZST occurrences
may share one numerical address; index inequalities are never address inequalities.

The negative keeps actual min/lo/max choices but replaces hi with min when all
replies are false, yielding IDs0,1,0,3. Failure must be at its marked `s4_perm`
assertion after the checked header theorem; parse/setup/other failure is inconclusive.
Ghost-only source has no executable runtime or unwind path, so Rust refinement is
inapplicable to this theorem. Ordinary dead-code/leak checks remain enabled.
