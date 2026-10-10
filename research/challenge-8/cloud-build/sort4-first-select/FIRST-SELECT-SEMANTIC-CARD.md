# First actual selector after the C4 prefix: conditional design card

This is a read-only next-step design, contingent on an accepted exact C4 bound
verdict. It does not admit a selector summary, verifier profile, proof or Cloud
dispatch. The actual source is `sort4_stable` from std blob
`40939f922bcb6fdc7ee0d30427fa861827043827`; the first selector is
`let min = hint::select_unpredictable(c3, c, a);`. Stop immediately after its
result and rejoin, before `max`, nested selectors, C5 and copies. The first six
selectors occur before C5; two occur afterward.

**Actual obligation.** C1–C4 have returned normally, with the four existential
CURRENT source cells, their `T.own` resources, `F`/thread/type resources and
optional destination frame preserved. C1/C2/C3/C4 direct-unwind exits still
reach their complete original posts without entering the selector. The first
selector must consume only its documented thread-token premise, return that
same token and a pointer equal to `if c3 { c } else { a }`, with the relevant
`raw_ptr_own<T>` result. The four CURRENT pointee owners remain a separate
frame; a raw-pointer result contract does not supply points-to or `T.own`.
Retain the source generic signature, original full normal/direct-unwind posts,
unit return, leak/dead-code/refinement checks and all runtime operations.

**Callee qualification.** The historical pointer-specialized actual
`select_unpredictable` proof is a conditional result in the separate
`NEXT-SELECT-FRAME-CALLER-CLOUD-2026-10-09` profile (Build
`f4dc1ddf-c995-4650-a4d0-896cf14ad565`), documented in
[`END-CHECKPOINT-2026-10-09.md`](../next-select-frame-caller/END-CHECKPOINT-2026-10-09.md)
and [`FINAL-TEST-RESULT.json`](../next-select-frame-caller/FINAL-TEST-RESULT.json).
It verified the actual pointer-specialized source, seven prefix callees and
nested Drop in one nine-body unit, including both Boolean returns, false
unwind, CURRENT thread token, selected original pointer equality,
`raw_ptr_own`, return and leak checks. Its profile remains unaccepted and its
tool differs: translator `9cf8bc328a2a12c97b9ae04b359f8a4c59f1d561ae768f1e6bde4146d247a041`,
kernel `adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`.
The current C3 chain has translator `d2f132148d409eb9a9e27afd24603d992405ec1984849817da9e427ab070db6e`
and kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Historical `o26-r3-frame-shadow-test.py` reconstructs its own exact old
R2/R3/FRAME/shadow/cleanup translator chain and cannot run unchanged against
the current frozen tool or qualify a summary for it.

The minimum new qualification is a fresh capture of the actual selector
source, full normal and readonly nine-body MIR, pre-AST, proof-unit/body hashes,
source/runtime identity, same-version callee contracts and proof order under
the **current** frozen tool profile. Running the callee separately is possible
only if the consumer's summary/link mechanism checks exact source, tool,
contract and type-specialization identity and the complete callee proof first;
same-unit proof is the simpler auditable route. Keep all C1–C4 experimental
scope flags off during a separate callee invocation, and preserve the
selector's own required opt-ins only after their trust/admissibility review.
The historical driver is useful as a source-capture and control template, not
as a reusable verified summary. No new kernel/parser/spec/memory/refinement
patch follows from this card.

**Falsifiable first-select experiment.** Freshly pin the C4-complete consumer
source/MIR/pre-AST and the qualified selector unit before any rewrite or proof.
Show callee proof before consumer linkage, then prove the first actual select
with `Element=T`, condition `c3`, inputs `(c,a)`, selected pointer equality,
thread-token handoff and the four-cell CURRENT frame. A wrong-result contract,
lost thread token, lost pointee owner or unqualified callee summary must fail
at its intended contract/link/resource obligation; source/tool/AST mismatch
must refuse before proof and does not count as a semantic negative. Inspect
complete Cloud logs for first stage, predicate and location. A positive
bounded prefix gives no C5, remaining-selector, whole-sort4 or actual caller
credit. Any selector frontend rule absent from the frozen tool requires a
separate trust decision before implementation.
