# R21 source-transport reduction investigation

This is a static source-closure recommendation only. No Cloud operation,
preparation, compiler, exporter, verifier, or reconstruction script was run.
The reported starting transport size (192/191 parts before c5) is supplied by
the task; this investigation did not regenerate that payload.

## Current route and identity checks

`recipes/o26-sort4-c1-current-recovery.json` is a broad historical recovery
recipe. Its exact infra transport is built from `EXACT_INFRA_CORE`, the recipe
`infra_paths`, and the recipe file in `cloud-build/source-input.py`;
`proof_paths` are selected separately from the proof checkout. Both sides
currently reference `sort4-caller-entry-native/selected-proof.py` (recipe
lines 83 and 147), once in each source record. `source-input.py:335-349`
globally pools shared objects by object ID across infra/proof records before
encoding them, so matching Git objects transfer their blob bytes once. Removing
the infra-side path would clean up one record/tree reference, but would not
remove a second 104 KB blob from transport.

The R17 recovery entry path is `a1-entry-r17.py` -> `a1-runner-r17.py` ->
`a1-actual-body-r17.py`. The entry pins the profile and caller manifest, then
loads the selected runtime, scope audit, ghost stripper, driver, and R17
runner. The R17 runner pins and loads the actual-body module. The full-body
branch does not call `driver.py`'s selected-prefix route: that conditional
loads `selected-proof.py` only for `session_mode ==
COMPILER_QUERY_AND_SELECTED_PREFIX` in the generic driver path. The actual-body
path does, however, use proof-checkout `a1-runner.py` at
`a1-actual-body-r17.py:491` for its single method
`select_checked_cleanup_helper_lemma`.

That generic runner is 254,532 bytes (4,440 lines); the proof-side
`selected-proof.py` is 104,716 bytes. The current R19 profile pins the generic
runner SHA-256 as
`b55f3049f10fc551a1fec1b3f72ec7219d0240366bc37e2e89435709510c0411`, and
the selected-proof SHA-256 as
`3347ad41c0273ebf186dbcf0520182455b32a65ad9619f2b2c7d3d00c12a7d7f`.
The R17 actual-body SHA-256 is
`5e745a6715ad58e2921bd6f93e3d768bbb10ec0b62143b1f307c2050ff15df1f`.

## Smallest safe reduction

For the existing recovery recipe, removing the `selected-proof.py` entry from
`infra_paths` is metadata cleanup only; retain its `proof_paths` entry and all
manifest/profile pins. The R17 full-body route does not invoke the generic
selected-prefix branch, but the current profile carries its digest and that
route remains supported elsewhere. The material size reduction is a new exact
lane that omits the unused 254 KB generic `a1-runner.py` blob after replacing
its sole R17 full-body use with the extracted, independently pinned selector
module; see `CLEANUP-HELPER-EXTRACTION.md`.

For a new R21/R22 transport lane, make a separate exact recipe and do not
reuse the historical recovery recipe as the new closure. The strongest
bounded reduction is to replace the R17 body path's import of the 254 KB
generic `a1-runner.py` with a small, independently pinned helper module that
contains only `select_checked_cleanup_helper_lemma` and its local AST-location
helpers (`_ast_source_span`, `_ast_source_coordinates`, and `_need`). The
method is roughly 80 lines; its dependencies are `hashlib`, `re`, and the
already-pinned `a1-ast-gates.py`. Keep all checks intact: metadata type/name,
exact source block digest and ghost delimiters, unique declaration, manual
lemma/trigger shape, header and close coordinates, unique effective AST
interval, and the `proof_credit: False` result. Bind the extracted module by a
new profile hash and import it from the actual-body path; leave the historical
R17 profile and generic runner untouched. This avoids changing a multi-route
artifact whose hash is used by older profiles.

The closure for that new lane should be derived from the selected profile's
actual `a1-tool-r17.reconstruct` patch/manifest fields and the R17 import path,
not by copying the current broad `proof_paths` array. Keep the pinned actual
source, caller manifest/phase gate, actual-body generator, capture helper,
checked copy/selector/recovery inputs, ghost grammar, reference-own probe,
fixture and AST helpers, driver, and runtime helpers that the route reads.
Exclude unrelated historical profiles, unused R15/R16 body runners, and
selected-prefix-only artifacts only after a static read-set check proves they
are not consumed by the selected R21 body action. The recipe must still carry
the R13 source/leak controls and exact source identity; transport trimming
cannot replace or weaken those gates.

## Invariants to preserve and validation

`a1-actual-body-r17.py:22-84` pins the std source bytes and requires the
complete body call inventory: five `is_less(` calls, eight
`hint::select_unpredictable(` calls, and four `ptr::copy_nonoverlapping(`
calls. Its generated body must ghost-strip to the entire original runtime
body. The normal and unwind contracts keep the sole `T` ownership sequence
on the source and distinguish initialized destination ownership from the
unwind destination state. Preserve those checks and all existing component,
resource/leak, helper-proof, and source-pair checks verbatim in any new route.

Before adopting the reduction, add/adjust synthetic tests to:

1. Assert the new exact recipe lists each required proof/infra path once and
   excludes the selected-prefix-only infra copy and unrelated historical
   runners.
2. Build a tiny synthetic source-input payload from fixture Git trees and
   verify the selected object set is exact, deduplicated within each checkout,
   and rejects a missing or hash-mismatched pinned helper/source.
3. Compare the extracted selector helper's acceptance/refusal cases against
   the current implementation, including malformed metadata, wrong source
   digest/bounds, ambiguous AST declarations/intervals, and bad coordinates.
4. Exercise source-level assertions for the five/eight/four call counts, full
   ghost-strip equality, source hash, and normal/unwind ownership posts; keep
   these wholly synthetic and do not claim proof credit.

These tests validate the source transport and admission controls only. They
must not invoke preparation, compiler/exporter/verifier, reconstruction, or
Cloud services. The immediate one-entry infra-path deletion can be separately
validated with the existing recipe/transport synthetic tests; no code or
recipe was changed during this investigation.
