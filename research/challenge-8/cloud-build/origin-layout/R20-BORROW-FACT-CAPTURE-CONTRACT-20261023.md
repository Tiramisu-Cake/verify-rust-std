# Original caller borrow-fact capture contract

Static investigation of tool `191a5cd` and diagnostic successor `37b83428`.
No compiler, exporter, decoder, refiner or verifier was run locally.

The active exporter callback `after_analysis` obtains and steals the selected
`mir_drops_elaborated_and_const_checked` body (`vf_mir_exporter/src/lib.rs`,
lines 225–259). Its body identity records DefPathHash, captured MIR phase and
captured MIR hash. The last is a DefaultHasher fingerprint over the debug body,
not a cryptographic source hash (lines 928–933 and 1713–1757). Region scope
combines DefPathHash and that fingerprint. Source/stage receipts provide the
separate exact source hashes. None of these fields supplies NLL liveness.

The query override, Polonius option, BodyWithBorrowckFacts collection and drain
are commented out. The dormant prototype stores compiler references through a
`static` lifetime transmute; it is unsuitable for reactivation as written.

The next capture implementation should preserve the selected query, exact
emitted MIR body and phase. At the borrowck query boundary, before later MIR is
stolen, serialize an owned fact projection; do not retain compiler references
in a static map. Bind its payload hash to the source-stage receipt, compiler,
driver arguments, DefPathHash, and the fact body's own phase/fingerprint.
Record the selected body's phase/fingerprint separately. Pinned compiler API
compatibility and whether its facts option affects capture are UNVERIFIED;
they require source/API investigation and Cloud checks within a later admitted
cycle, not an assumed API or an extra trusted premise.

A fact row becomes usable only after exact body/point identity is established,
or an explicit point/CFG map is validated. Matching DefPathHash or regionScopeId
alone does not join pre-elaboration facts to a later cleanup body. Keep original
and verified mappings independent and compare normalized facts at refinement.
Required rows cover the exact Ref, array-to-slice Unsize, as_mut_ptr call and
all normal/cleanup/unwind successors, with scoped region variable and stable
MIR point IDs. StorageDead alone does not establish an NLL end.

Discriminating controls must reject wrong scope with the same variable ID,
wrong variable ID, missing/erased identity, phase or body mismatch, changed
source/fact hash, invalid point map and omitted unwind edge. Capturing facts
must leave selected runtime MIR and its identity unchanged. Missing binding is
INCONCLUSIVE. Facts alone create no memory authority, full_borrow or semantic
lifetime. The existing checked borrow/borrow_end protocol must still consume
and restore the same owned concrete resources; representation helpers only
convert content when those resources and an existing borrow are present.

The prepared immediate HANDOFF candidate adds diagnostic context only. This
capture contract is a later obligation, not an implemented exporter feature or
an acceptance claim. Original caller, CURRENT matrix and independent credit
remain OPEN.
