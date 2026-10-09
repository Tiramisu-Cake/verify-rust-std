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
