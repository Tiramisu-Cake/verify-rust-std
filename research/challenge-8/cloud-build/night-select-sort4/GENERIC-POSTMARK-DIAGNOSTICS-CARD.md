# Combined generic constructor and sort4 post-mark Cloud diagnostics

The `o26-generic-sort4-postmark-diagnostics` lane runs the unchanged canonical
O26 refreshed baseline once, then requests two independent diagnostics in
the same identified Cloud Build. `generic-new-capture` records the separate
source-local generic `MaybeUninit::new<T>` body, a distinct external std call,
paired MIR and refinement. `sort4-postmark-print-test` copies the production
O26 tool, applies only the opt-in print patch to its disposable
`src/verifast.ml`, and observes actual sort4 locals after
`stmts_mark_addr_taken`. They have separate evidence directories and result
files. Neither diagnostic supplies a summary or proof to the other.

The generic source certificate and no-proof boundary are fixed by
`overnight-generic-select/CLOUD-GENERIC-NEW-SOURCE-CARD.md`. The post-mark
kernel-file TEST trust boundary, full actual sort4 source/MIR/refinement
pins, off/on expected `verified/lib.rs(185,13-36)` first refusal, and lazy
`locals_to_free` limitation are fixed by
`overnight-callback/CLOUD-ACTUAL-SORT4-POSTMARK-PRINT-TEST-CARD.md`.
Normal/readonly export, decode and refinement failures, source or tool
drift, missing local/owner/type data, changed AST bytes, or changed first
error make the relevant diagnostic inconclusive. The post-mark patch does
not change proof operations, but its verifier-core instrumentation is an
isolated TEST profile, never production.

Only the two explicit flags are on: `O26_WITH_GENERIC_NEW_CAPTURE=1` and
`O26_WITH_SORT4_POSTMARK_PRINT_TEST=1`. Owner/A1, CUT/strictCUT/false-posts,
old AST probe, blocked AST-scope TEST, wrapper/R3, coordination and actual
sort4 proof modes remain off. The outer audit must require the complete
canonical baseline and both independent helper classifications; its
`diagnostic_complete` can be true only after both pass. It always reports
`verification_accepted=false`, `accepted=false`,
`actual_callee_proved=false`, `generic_constructor_helper_proved=false`, and
`storage_cleanup_proved=false`. The existing canonical O26 proof headers
retain their own historical meaning but cannot promote these diagnostics.

The exact-recipe-v1 proof input set is the complete existing generic lane
set, the three new post-mark proof files, the pinned actual
`smallsort.rs`, and precisely the six existing transitive proof files
required by `actual-sort4-capture.py`. It includes no CUT/lifetime TEST
patches or unrelated recovery diagnostics. The infrastructure input set
extends the generic lane with the new wrapper/card, post-mark runner/audit,
`actual-sort4-capture.py`, and its `sort4-ast-audit.py` preflight dependency.
The canonical and generic lane recipes are also selected infrastructure
inputs so exact-transport controls can check the full parent proof closure.
The refresh patches and source-input/exact-transport
controls remain required. No new tool, dependency download, or production
source build is requested beyond the already necessary canonical O26 build;
the post-mark console rebuild is confined to a copied tool tree using the
same installed dependencies.
