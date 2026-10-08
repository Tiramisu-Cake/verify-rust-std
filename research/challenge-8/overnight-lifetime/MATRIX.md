# 26.10 strict lifetime-cut hosted matrix

This is a proposed acceptance matrix; no 26.10 case has been executed. The
copied and reviewed fixture source is [cases.rs](cases.rs), derived from our
historical 26.09 controls, with a new same-unit verified callee/direct
unwind case. The historical runner itself is not portable: it pins
nightly-2026-02-05 and a fixed `/tmp/vfdeps-adf88dc` decoder, and its
duplicate-marker message differs from this candidate's one-marker-per-body
rule. Do not count an old 26.09 PASS as evidence for this patch.
The new hosted capture sets `SORT4_STRICT_LFT_CUT=1` only for this matrix.
An unmarked/control invocation with that variable absent must preserve the
stock route; a marked invocation without it must reject before proof.

Each selected case needs a fresh isolated verified source and a ghost-stripped
original. Record both hashes and exact strip identity, source SHA and target
name(s), compiler/tool/prelude/patch hashes, complete NORMAL and readonly
binary and decoded MIR, stages, refinement, full VF log and result, and the
first failure. `positive_direct_unwind` intentionally has **two** source
bodies: `cut_maybe_unwind` must itself verify through return/leak check before
its summary is used; the target must verify both normal and direct-unwind
posts. All other cases select one body. Export/decode/refinement failures are
inconclusive. A negative is classified only when the positive setup reaches
its named admission or proof obligation; a parse failure unrelated to the
cut, missing summary, or failed source integrity is inconclusive.

| Case | Expected exact boundary |
| --- | --- |
| `positive_basic` | Full VF0, binding half restored at marker, one `end_lifetime`, no leak. |
| `ordinary_unmarked` | Full VF0 with stock lifetime closing at the real brace; no cut marker, no changed resource post. |
| `positive_early_return` | Full VF0 on early return and normal cut path; no second half release. |
| `positive_direct_unwind` | Full VF0 for callee and target; actual call direct Continue, normal and unwinding returns consume full lifetime token. This is a candidate until hosted MIR confirms direct Continue. |
| `positive_f_bound` | Full VF0 for an isolated copy of the hosted `callback_positive` resource protocol, with the cut inserted after its only FnMut call. Its function DefPath remains `callback_positive`, the only name admitted by the already accepted callback hook; the HRTB matcher is enabled for this body only. Normal and unwind resources and comparator owner must close, and the outer `F` bound must rebase to its frozen entry value. Its complete MIR and proof trace need review before counting it. |
| `negative_wrong_marker`, `negative_marker_outside_binding`, `negative_unknown_binding` | Exact `end_lft_binding needs one enclosing ghost block containing only its let_lft declaration` admission error, before body proof. |
| `negative_nested_marker` | Exact enclosing-block admission error with two active `let_lft` declarations. If exporter does not preserve both blocks, classify setup inconclusive. |
| `negative_malformed_marker` | Exact `expects exactly one named lifetime type and no arguments` admission error, before body proof. |
| `negative_duplicate_marker` | Exact `Strict lifetime binding expects exactly one cut marker per body` admission error; no proof classification from setup. |
| `negative_type_name_after_cut`, `negative_type_argument_after_cut` | Post-cut scoped type/name rejection, after a valid cut was admitted. |
| `negative_typed_chunk_survives_cut` | Exact strict kernel live-ending-type heap-chunk error; never silent discard or leak PASS. |
| `negative_unclosed_fractional_access` | Missing full token at assertion/end_lifetime after cut; checked fraction was not closed. |
| `negative_reserved_half_after_lifetime_end`, `negative_end_lifetime_twice` | Missing token at second use; verifies exactly one reserved-half return. |

Additional acceptance controls still need source fixtures and separate hosted
classifiers: incoming CFG edge into the prefix or synthetic entry after the
cut, outer variable whose type retains `'cmp`, a live nested bound on a
non-outer type parameter, and unresolved/late-resolving inferred metadata in
the entry or exit bounds, heap, or outer variables. A failing fixture must
expose the intended checker, and the corresponding lawful variant must pass.
The source position mutant must give the marker and the enclosing exporter
declaration block different file paths and fail before AST reconstruction.
Use a disposable exporter wrapper only for that negative: export the unchanged
positive source with the pinned real exporter, decode the complete selected
body, change exactly one `ghostDeclBlocks[0].closeBraceSpan` file path, then
encode the typed MIR. Retain original and mutated text/binary, hashes and a
one-field mutation record; independently run original compilation and
refinement on the unwrapped source. A decoder/encoder error or any source
mutation is inconclusive. The strict gate must reject the mismatched file
before function proof starts. A separate wrapper may redirect exactly one
successor in the selected positive graph to a prefix block to test CFG
ingress/reentry; its block IDs and expected rejection must be pinned from
fresh paired 26.10 MIR rather than guessed from historical output.
The new translator also rejects any path from the cut continuation back to
the synthetic entry; an ordinary enclosing loop needs its own reviewed
certificate, not an implicit exception. An
unmarked ordinary Rust block, a normal callback, an unmarked direct unwind,
and shared-cleanup/Drop control must retain their stock AST and proof result.
The existing overnight S6 full matrix and callback/H2b controls are required
after this patch is added to the combined profile; a local lifetime matrix
alone cannot establish noninterference.

For the opt-in boundary, run `capture.py --case positive_basic --without-opt-in`
in a **separate fresh output directory**. Its exact source and paired MIR
must still export and refine, and full verification must reject the marker
with the explicit opt-in message before proof. `ordinary_unmarked` should
also run in the default matrix; the default matrix's opt-in variable must
not change its stock result.

The runner records SHA-256 of both complete decoded MIR files for every
source case. It rejects any change to the reviewed `cases.rs` template SHA-256
`7cb5c8a8a2541da30af188c8731ee13276c59b206e5ed58a78e909852719359e`
before export. MIR hashes are evidence fingerprints, not pre-reviewed
certificates. The exact source/body path, complete graph, cleanup inventory
and intended first error for every new escape/CFG mutant must be reviewed
before replacing its `INCONCLUSIVE` classification with an intended negative.

The next actual-sort4 experiment must add the marker and a separately
reviewed checked resource-recovery sequence. This component alone changes
only scope mechanics. It has no license to weaken the full unwind post,
promote the partial normal destination post, or claim generic/ZST safety.
