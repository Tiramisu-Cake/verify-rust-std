# Native source-pair turnover resource fixture

This fixture isolates recursive extraction and restoration of two **current**
owners at native-`usize` indices in an owned positive-stride array. It contains
four cases: current-value extract/restore, same-pair turnover, arbitrary
overlapping-pair turnover, and a matched full-domain false-entry control. It
does not call `bidirectional_merge`, perform runtime element reads/writes, or
derive the resources from a caller. The source and destination frame chunks,
current `F`, owner resources, and complete normal/unwind posts stay explicit.

The recursive ghost index is `option<usize>`; each descent uses checked
`native_pair_index_step_in_range` and `native_pair_ordered_step`. The array
domain requires `0 < size_of::<T>()`, `n * size_of::<T>() <= isize::MAX`,
nonwrapping span arithmetic, and valid base/one-past pointer limits. The
selected predicates preserve the exact current values and their unique
`<T>.own` chunks. This is a component-level resource fixture, not evidence for
the actual callback frame, source-slice ownership bridge, or generic ZST path.

## Parser-stage repair and evidence boundary

### RESOURCE10 pure range/order preconditions

The a643d1e1 run reached VeriFast but stopped while parsing the first native
helper contract: `native_pair_index_in_range` was reported as an unknown
predicate. The name is a `fix` returning `bool`, so it is a pure condition, not
a resource predicate. The same issue affected the pure ordered/distinct and
current-value match conditions in the helper contracts. Spell each such
condition explicitly as `... == true` while retaining `&*&` only to separate
the existing resource chunks and pure facts. This is a grammar/type-category
repair: it keeps every range, ordering, and current-value condition, and leaves
all resources, helper bodies, and normal/unwind posts unchanged. Fresh hosted
evidence is required; this draft has no proof result from the repair.

### RESOURCE10 parse-syntax follow-up

The 54a22b0d run confirms that the earlier multi-line `/*@ ... @*/` wrapper
commands still fail at VeriFast parsing before any fixture/helper body is
entered. For the current-value extract/restore case, the diagnostic points at
the second `native_pair_restore` command; the native turnover cases similarly
point into their multi-line ghost command sequences. The permutation positive
and matched false-entry cases passed in both profiles with the single-line
`//@` command form, while its double-owner calibration stopped at the first
command inside a block annotation.

This follow-up changes only wrapper command spelling: each existing ghost
lemma/assertion command becomes one complete single-line `//@` command. It
does not alter the checked helper prefix, contracts, resource predicates,
domain assumptions, normal/unwind posts, or calibration assertion. The
expected checked prefix bodies therefore remain the same; only the fixture
wrapper command syntax changes. The false-entry marker remains at columns
16–21. Remove the fixture's Rust `allow(dead_code)` attribute: verifier dead
code checks remain active independently of Rust lint settings. This is a
syntax-only draft and requires a fresh hosted run; the calibration remains
unclassified until a later run reaches and localizes its intended owner
assertion.

In f0b1ff62, exporter, Cap’n Proto decode, and refinement succeeded for both
stock and experimental profiles, but all four cases stopped at VeriFast
parsing with zero visited fixture/helper bodies, zero return records, and zero
leak checks. The blockers were continuation-style `//@` calls split across
source lines (first reported at `verified/lib.rs:296`, then `:301` and `:303`);
the false-entry control therefore did not reach its `assert false` and is not
a negative result.

Those multi-line ghost command sequences now use a single `/*@ ... @*/` block
inside each Rust body. The arguments, lemmas, assertions, cases, domains,
resources, and posts are retained. This is only a grammar repair; it has no
proof outcome until a **new** hosted run reaches the expected functions.

The next hosted inventory should expect all four case bodies plus
`native_pair_replace_length`, `native_pair_index_step_in_range`,
`native_pair_ordered_step`, `native_pair_extract_rec`,
`native_pair_restore_rec`, `native_pair_extract`, and `native_pair_restore`.
Positive acceptance requires each expected body, normal return, leak, source,
refinement, and dead-code gate. Count the false-entry control only if the
predeclared full-domain target executes and fails at its exact `assert false`
predicate and location. A parse, exporter, decode, unrelated helper, or source
admission failure remains inconclusive.

## RESOURCE11 empty-suffix option-index proof repair (candidate, unrun)

Fresh Build `3a000599` / proof `07d0dc5` confirms the pure boolean range/order
contracts are admitted: all three pure helpers pass in both profiles, and the
first three helper bodies are visited. The first failure is the intended
`native_pair_extract_rec` close of `native_pair_selected` at generated
`verified/lib.rs:81:11–13`: VeriFast cannot prove `i == none`. In the recursive
base branch `n == 0`, `native_pair_selected` requires both option indices to
be `none`, while the helper preconditions only give
`native_pair_index_in_range(i, n) == true` and the corresponding fact for `j`.
The range definition makes `some(k)` impossible at zero length, but the current
body does not explicitly split/unfold that case before closing the predicate.

Candidate repair: inside only the `n == 0` branch of
`native_pair_extract_rec`, explicitly match each option index. The `none` arm
continues directly. In a `some(k)` arm, expose the range fix's definition
(`0 <= k && k < n`) from the unchanged range precondition and use `n == 0` to
discharge the arm as contradictory. Then close the same holes and selected
predicates. This adds no precondition, assumption, axiom, arithmetic cast,
resource conversion, or postcondition weakening; it preserves full source
ownership, current values, all frame resources, and the native-`usize` domain.

Static review of the corresponding `native_pair_restore_rec` base branch shows
that it first opens `native_pair_selected`, which itself yields `i == none` and
`j == none` as pure facts when `n == 0`. Its subsequent owned-array close does
not require a fresh range-to-option derivation. Keep that branch unchanged
unless a new hosted failure gives contrary evidence. This does not claim its
body has been verified; it was not reached in Build `3a000599`.

The proposed candidate is unrun. Its next hosted run must check both profiles,
all four case bodies, and the full expected helper inventory, including return,
leak, source, refinement, and dead-code gates. In particular it must reach
`native_pair_restore_rec` and the wrapper cases. A failure to prove the explicit
range unfolding, any other helper/body failure, or a failure before the
full-positive gates is inconclusive and requires reading the complete Cloud
evidence. The matched false-entry counts only at its existing target. No claim
about the actual SmallSort caller or source-pair turnover is licensed by this
local proof repair.
