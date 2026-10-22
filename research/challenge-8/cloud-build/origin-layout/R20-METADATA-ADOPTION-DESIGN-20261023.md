# R20 metadata and checked-content candidate

The original caller loses coercion and region metadata before its unsupported
borrow/unsize path. Tool `191a5cd86745a84fbbc7b202661ad664b3cb272e` adds typed
source/target/coercion data and body-scoped inference-region metadata. The
translator does not consume these new fields; no lifetime, provenance, memory
authority or acceptance rule follows from them. Static tool review is GO;
compiler/API and generated decoder compatibility remain Cloud-UNVERIFIED.

The profile changes only effective tool, exporter, schema and cumulative patch
pins plus exact metadata registration. Reverting these fields must reproduce
R19 profile SHA `1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb`
and then pass the unchanged R19/R17 validators. The cumulative patch is the
exact `git diff -U1 f2e92cec..191a5cd` output. Its final ordered-chain slot stays
in place; all prior patches and translator/kernel/refiner/model pins stay fixed.
The provider changes only its onecell `prove.py` digest. The client admits only
the exact old tuple or registered new tuple, not an arbitrary manifest. Closed
ledgers, R13/R14 publication gates, budget/window, execution/reserve and transport
limits remain unchanged. GLUE-PROFILE changes only under this exact reversion
check; historical Build records keep their original profile identities.

Recipe delta from R20 P2 adds the metadata admission service test and checked
content helper. It omits five dormant synthetic service-test inputs:
`r5-emitter-service-test.py` (8,201 bytes), `r9-phase-service-test.py` (7,345),
`r10-invariant-service-test.py` (3,552), `r10-phase-service-test.py` (7,035),
and `r9-marker-service-test.py` (6,354). A dependency audit of active
`run-proof.sh`, `run-merge.sh`, `merge.sh`, selected `prove.py`,
`first-callback.py`, `control.py`, and the R13 synthetic-upload dispatcher
found no calls to these five files. The R8 wiring, R8 freshness, and
tool-evidence service tests remain because `merge.sh` invokes them. The earlier
reviewed R9 controls service-test removal remains; its references in dormant
R9/R10 source-preflight inventories are preserved. Only recipe inclusion
changes: files remain in the repository, and active control/preflight sources
remain intact. The committed candidate's final encoded payload is checked
against the existing transport limit.

The separate checked-content helper is described in
`R20-CHECKED-SLICE-CONTENT-DESIGN-20261023.md`. It is included in the raw caller
suffix behind an exact file SHA check, leaving the actual parent body and
normal/unwind posts intact. All lemma bodies require Cloud verification. This
does not establish the original array-reference lifecycle or repair its cast.

P1 also exposed a reporting defect: the raw positive classification inherits
`verifier_target_observed=false` from the isolated-body result constructor,
whose success name differs. Set this flag only for the already strict
`RAW_LOCAL_CALLER_BOTH_TARGETS_EXIT0` classification. Missing targets, source/
stage mismatch and nonzero stages remain inconclusive with the flag false.
Acceptance and all proof-credit flags remain false. Historical P1 records are
not rewritten; its precise observations retain the original contradictory flag.

Validation is bounded synthetic admission/source/receipt testing and static
Git/hash checks locally. Actual compile, metadata export/decode and required
controls stay Cloud-only. No independent proof credit or generic qualification.
