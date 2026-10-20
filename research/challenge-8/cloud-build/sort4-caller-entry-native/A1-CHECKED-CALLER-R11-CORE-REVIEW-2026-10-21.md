# Independent R11 core review — 2026-10-21

**Decision: GO for the bounded R11 Cloud hypothesis, after the parent refreshes
the source/profile pins to the reviewed files.** Review covered the R11 changes
to `a1-runner.py`, `a1-focus-backend.py`, `a1-tool.py`, their R11 activation
profile, the false31/core tests, and the P1 `a1-ast-gates.py` plus synthetic
AST tests. No proof credit is granted by these changes or tests.

## R11 target authorization and matrix controls

The target remains exact-phase scoped. `preflight_plan` accepts only the
existing R10 authorization or the exact R11 authorization when
`execution_mode == native-p1-target`. The R11 profile retains the established
protocol phase, `profile_accepted: false`, 26 `NOT_RUN` matrix entries, and
`proof_credit: false`. It does not become a dispatch-ready or full-matrix
profile. Both consumer maps (`a1-focus-backend.py::PROFILE_BINDINGS` and
`a1-tool.py::FOCUS_PROFILE_NAMES`) add only the exact R11 phase/profile pair.
`validate_profile_binding` still checks the coordinator environment phase,
authorization, exact profile bytes/hash, decoded profile equality, protocol,
pin source, cloud flag, and unaccepted status. The R11 adapter separately pins
the core runner and installs the R11 auth/profile constants before invoking it.

## Report serialization

The serializer adds R11 to the existing exact R9/R10 allowlist. It transforms
only an object whose embedded authorization equals the argument, whose details
are a mapping and rows a list, and which has no prior serialization marker.
Rows must have unique string case IDs. It replaces a row observation only when
both values are mappings and recursive equality requires identical Python/JSON
types as well as values. Missing, null, malformed, or conflicting fields remain
inline; malformed rows, duplicate IDs, or conflicting values return the
original object unchanged. JSON Pointer escapes `~` and `/`, every referenced
detail remains in the report, and conversion copies rather than mutates the
in-memory value. The marker explicitly records `lossless: true` and
`proof_credit: false`. Tests exercise JSON scalars (including bool/int/float
distinctions), nested values, Unicode and pointer escapes, source bytes,
immutability, partial rows, conflicts, duplicates, malformed values, and
cross-phase calls.

## Own false31 caller binding

`_false31_source_boundary` first requires `binding.caller ==
a1_guard_observer`, then a well-formed, ordered, in-range MIR body span whose
two endpoints name `verified/lib.rs`. It finds exactly one literal inclusive
threshold guard and one `len <= 31` assertion inside that span, ordered guard
before assertion. The existing paired caller structure supplies this binding;
the observed threshold MIR call must still land on the selected guard line.
The actual caller AST is then passed through `select_focused_body`, which
requires exactly one definition named `a1_guard_observer` whose AST source and
closing-brace intervals equal the compiler body span. The checked common
threshold prototype and its inventory source line/contract checks remain in
place. Thus the original quicksort guard outside the observer cannot create a
false ambiguity, while duplicates or reversed order inside the selected caller
still fail closed.

The own false31 receipt/body flow is not changed: a boundary observation still
depends on the paired N-false31 source, compiler-bound caller structure, and
checked threshold contract. This is an observation fix only and does not
reclassify earlier evidence or add proof credit. Synthetic tests cover outside
duplicates, in-span duplicates/reversal/missing entries, wrong caller/path,
invalid endpoint types/ranges, and invalid spans.

## P1 AST identity and diagnostic change

The exact qualified-local allowance is limited to the two canonical fields
`<T as StableSmallSortTypeImpl>::small_sort_threshold` and
`<T as StableSmallSortTypeImpl>::small_sort`, and only under an empty root
`PackageDecl` owner. The complete local string is retained as the name. Bare
locals continue to be qualified by their package owner. A qualified local
under any owner, an unrelated qualified spelling, and an unsupported type
spelling still raise `AstGateError`; duplicate `small_sort` records remain
separate records and preserve their source spans for downstream compiler-item
selection. The synthetic controls check both positives, duplicate bodies,
verbatim names/spans, and invalid-owner/invalid-name negatives. No first/last
selection or leaf-only matching was introduced.

On rejection, the new helper retains the original `AstGateError` class and
`package Func local name` reason; it adds a bounded preview, lengths, and a
digest for owner/location/local context. It is a pure formatter over already
parsed values and does not evaluate source expressions. The positive
qualification rule is a separate narrow parse representation correction, not
a change to prototype/body, contract, source-span, compiler-ID, or proof gates.
The evidence-indexed R-only AST representation is the rationale for this
specific root-qualified form; its parser-input binding to the reported P1
failure remains unestablished, so Cloud must still falsify/confirm applicability.

## Validation and limits

Passed isolated Python checks from `sort4-caller-entry-native/`:

- `python3 test_a1_ast_gates.py` — 34 tests passed.
- `python3 test_a1_r11_core.py` — 3 tests passed.
- `python3 test_a1_r11_false31_boundary.py` — 3 tests passed.
- `git diff --check` — passed.

The package-module unittest invocation initially failed because its package
path uses hyphens; rerunning from the test directory succeeded. No compiler,
verifier, source extraction, full preparer, Cloud Build, or raw evidence was
run or inspected. Before submission, refresh the R11 profile's helper and
runner SHA pins and rerun the existing activation/error-path tests on that
final pinned profile. The Cloud result must still be reported through the
Evidence Brief and kept separate from setup work and independent proof credit.
