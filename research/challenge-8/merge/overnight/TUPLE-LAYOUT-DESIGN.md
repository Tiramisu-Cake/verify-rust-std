# G2 nested tuple entry-death diagnostic

Run 37750163906, pinned to its recorded source/tool profile, does not verify
the isolated `trace_nested_tuple_original_domain`. The exporter, decoder and
refiner finish, but VeriFast reports every body location as dead, with zero
body execution, return and leak records. The same generic pointer/index/choice
precondition in `trace_generic_entry_domain` reaches two assertions and passes.
The original `g2_pointer_trace_projection` shows the same entry death while its
twelve helper bodies remain separately reachable; those helper passes do not
establish the G2 function.

The proof AST of the failing isolated case begins with an uninitialized
`DeclStmt $_0` of the exact nested `G2PointerTrace<T>` return type, followed by
an uninitialized four-pointer tuple `$_8`. The original G2 AST also begins
with the same nested `$_0`, but its next declaration is unit `$_8`. Both logs
print only two entry `Executing statement` records after the function lifetime
token, then dead code. The common suspected transition is production of the
uninitialized nested return-place object. The logs do not identify which
assumption made the path inconsistent, nor do they prove that tuple depth alone
is responsible.

The stock kernel routes each uninitialized `StructType` local through
`produce_object` and `produce_cxx_object`. `produce_c_object` recursively
produces padding and field chunks for nested structs and assumes
`field_pointer_within_limits` for nested fields. Tuple types are translated
as `std_tuple_N_` structs. These are candidate mechanisms to discriminate,
not an identified defect or permission to change the kernel, prelude or
translator. The original twelve-field trace return and normal/unwind posts
must remain the target; no `assume(false)`, dead-code exemption or weaker post
can count as a repair.

## Hosted diagnostic ladder before a fix

Use independently extracted fixtures under the same generic entry domain,
with a complete value-specific normal post and `on_unwind_ens false` for each
return type. Preserve source/MIR/refinement checks. At each step record the
proof AST's first declarations and exact body/return/leak/dead-code counts.

| Return type and constructor | Question isolated |
| --- | --- |
| `()` | Existing reachable baseline |
| `(*const T, *const T)` | First tuple-2 of raw pointers |
| `((*const T, *const T), (*const T, *const T))` | Second pointer-tuple depth |
| `((usize, usize), (bool, bool))` | Nested scalar fields without generic pointers |
| `(((*const T, *const T), (*mut T, *const T)), ((*const T, *mut T), (*const T, *const T)))` | Pointer half of the trace |
| Exact `G2PointerTrace<T>` | Both halves and original twelve-result shape |

Add an independent `assert false` entry probe for each type to classify
reachability at its intended assertion, never as a positive. If a smaller
type already dies, inspect the first failing declaration and compare the
same type as a local with unit return, and as a return without a constructor.
This separates return-place allocation from aggregate construction and post
selection. A source-level split into multiple return values is only a
diagnostic: it cannot replace the unchanged G2 target.

A semantic fix is justified only after a specific contradictory stock
assumption or layout equation is exhibited and reviewed against Rust tuple
layout/provenance. It needs a distinct trust review and affected regression
matrix before implementation. Until then, the minimal valid next action is
the hosted ladder, not a verifier patch.

## Entry-reachability tuple-shape fixture

`tuple-layout-cases.rs` isolates the entry-death hypothesis with eleven
independent ordinary unsafe functions, all with `req true`, complete
value-specific leaf posts, and `on_unwind_ens false`: a unit assertion-false
baseline; positives for a flat raw-pointer pair, paired raw-pointer pairs,
nested scalar pairs, the eight-pointer half of the original trace, and the
complete twelve-leaf G2 tuple; and one assertion-false entry probe for each
non-unit shape. Each negative duplicates the corresponding positive's return
type, precondition, postcondition, and tuple constructor, inserting only
`assert false` before the constructor. `TARGET` markers identify those
assertions, but no error oracle is guessed; all five remain uncalibrated until
a hosted log reaches each exact marker.

The shape order distinguishes first tuple allocation, deeper product nesting,
generic raw-pointer leaves versus scalar leaves, and the full return layout.
All posts name every output leaf; selectors are parenthesized to avoid numeric
tuple-field lexical ambiguity. The fixture has only type aliases for the two
nested product shapes and introduces no logical helpers, tuple own axioms,
`assume(false)` escape, or runner classification bypass. Dispatch the fixture
through the existing CASE-isolating pointer proof runner. Require all positive
cases to report one expected body, body execution, return, leak check, and no
dead-code records; require unit plus each negative to reach its own marker at
the expected assertion before adding exact error metadata. Preserve source
equality, exporter, decoder, and refiner gates for all eleven cases. These are
diagnostics only: they do not repair or replace the unchanged G2 trace target.

## Alternative complete stock layout, before hosted run

The original tuple2 tree remains intact. Add a tuple3 of three tuple4
components: `(left,right,dst,left_rev)`,
`(right_rev,dst_rev,left_end,right_end)`, `(a,d,odd_left,guard)`. These
are all twelve original coordinates in the same order with two selectors
per leaf. The stock prelude already declares tuple3 and tuple4; no generated
`#assume(false)` lemma is admitted and no new semantic patch is added.
`pointer-trace-quartet-cases.rs` keeps every original domain premise, complete
postcondition, checked helper body, loop step, negative index wrapping and
terminal guard. Only the type alias, return grouping, selector map and case
name change. This is an independent diagnostic, not a proof transferred from
the original layout.

The ladder adds the same complete twelve-leaf constructor and an assertion
false before its first statement. Hypothesis: reducing tuple allocation depth
allows body entry while preserving all outputs. Positive acceptance still
requires all body/return/leak/dead/source/export/decode/refinement gates. The
negative must reach its TARGET before an oracle can be calibrated. If both
remain dead, pursue allocation initialization rather than inventing a tuple
summary; if they enter, continue arbitrary-length geometry obligations.
