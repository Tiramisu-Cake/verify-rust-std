# R21 cleanup-helper selector extraction

This extraction is inactive transport code. Nothing imports it from the
existing R17 route, and it does not award proof credit or perform any build,
preparation, compiler, exporter, verifier, or reconstruction work.

`a1-cleanup-helper.py` contains only the verbatim definitions of `_need`,
`_ast_source_span`, `_ast_source_coordinates`, and
`select_checked_cleanup_helper_lemma` from the pinned generic runner, with
minimal imports (`hashlib`, `re`, `Any`, and `Mapping`). The new synthetic test
compares the exact source text of each function against `a1-runner.py`, then
checks output/refusal parity against the original function with the existing
`a1-ast-gates.py` parser API.

The module SHA-256 is
`9af1324a6479896fd43eac8b8ccc3af3a254f28f672ffd4f99f0292cafaf3c45`; it is
6,660 bytes. The extracted functions retain source metadata identity, exact
ghost-block digest and delimiter checks, unique declaration matching,
manual-lemma/no-trigger gates, header/close coordinates, effective interval
uniqueness, original exception messages, and `proof_credit: False`.

The generic `a1-runner.py` is 254,532 bytes. A new R21 exact recipe can omit
that blob once the new route imports this module and binds the module hash in
its profile. The route must leave the existing R17 profile/runner unchanged
and retain the actual-body source pin, five/eight/four call inventory,
source-pair and ghost-strip controls, normal/unwind ownership checks, and
resource/leak checks. The review must derive the remaining recipe closure from
the route's actual read/import set; this extraction alone does not establish
that closure.

Transport correction: `source-input.py:335-349` globally pools Git objects by
object ID across infra/proof records before encoding shared objects. Therefore
the historical recovery recipe's two `selected-proof.py` path references do
not duplicate the blob bytes when both Git objects share the same ID. Removing
the infra-side reference is metadata/record cleanup, not a roughly 105 KB
payload reduction. The material transport reduction is omitting the generic
runner blob from a new exact lane; any measured byte/part delta still needs a
synthetic payload calculation for that lane.

## Validation

Ran `python3 -m unittest -v test_a1_cleanup_helper_extract.py` from
`cloud-build/sort4-caller-entry-native`: all 6 tests passed. The tests cover
verbatim extraction, accepted source/AST and external-definition cases,
metadata/source-hash/bounds refusals, delimiter and duplicate-declaration
refusals, AST interval ambiguity, manual lemma/trigger controls, and bad
header/close coordinates. These are synthetic parity checks only; they do
not establish formal proof or transport-size credit.

## Remaining integration steps

1. In a new R21 route only, import `a1-cleanup-helper.py` and call its selector
   instead of importing `a1-runner.py` for this single method.
2. Add the helper's exact SHA-256 to the new route's profile and add the helper
   to that lane's exact proof recipe.
3. Remove `a1-runner.py` from that new lane's closure only after a source-read
   audit and synthetic exact-recipe test confirm no other route dependency.
4. Run synthetic recipe/source-input checks to measure the resulting source
   object/part counts and reject missing or mismatched pins.

No integration, recipe/profile change, or commit was made here.
