# Review card: merge incoming-span lifetime primitive

Owner: merge. Active development location: isolated /root/verifast-merge-incoming-span,
branch merge/incoming-span-lifetime-20261009. Maintainer checkout/task untouched.
Base: f76012fb518703b1d98e243ac4f487f16877cfcb.
Portable tool commit: 75099c958eb6a6d46016babf0a845a624f77d9ab.
Old commits2f61f966/8c1386a8: NOT_FOR_INTEGRATION, not ancestors of this candidate.

Authorization: current user task MERGE-INCOMING-SPAN-LIFETIME-CLOUD-2026-10-09,
new3600s budget,60min main +30 finishing only; internal review publication permitted.
No upstream PR, maintainer message, integration, receipt or common-profile acceptance.

Rule: actual MIR StorageLive creates the address-taken local; StorageDead consumes
its existing full/immutable-half physical storage and removes its current path-local
binding. Only an unchanged physical entry Chunk still in current h may anchor
fixed scalar/pointer separation. No snapshot-only, raw parameter, provenance or
fresh-symbol exclusion. Calls that consume/recreate authority lose anchor eligibility.

Trust: translator lifecycle lowering and kernel storage bookkeeping/geometry.
No exporter/prelude/copy-contract changes; no new byte fractions, initializedness,
reference tokens or T.own. Allocation/death use existing production/cleanup rules.
Readonly aliases, owner resources and leak/unwind checks remain obligations.

Actual limitation: generic extents are excluded because the current layout model
can specialize sizeof(T)>0 to true for actual zero-sized structs/unit. The existing
strong raw-tail caller ownership/validity/type/thread premises remain supplied.
Generic actual separation, recovery/CURRENT association, cleanup/posts, Drop/glue,
comparators and whole insertion are separate open gates. No557/558 experiment.

Review requested: evaluate the lifecycle primitive and fixed-size rule under the
bounded controls; decide the minimum independently sound runtime byte-extent bridge
required before any generic rule or actual consumer admission. Do not integrate this
research candidate solely on control results. Exact fresh results are in checkpoint.

Final status: NOT_FOR_INTEGRATION. In addition to the excluded generic extent
domain, spelling-based lifecycle CallExpr markers have an unresolved origin
gate (extern-prototype/diverging source call may forge an event). This is static
review evidence, not an executed exploit. Six mechanism controls match in
cae0f3cc-9ca4-4ceb-b570-ab5e26e6ce82; all five actual cases stop before FBC at
line69 and are INCONCLUSIVE for their intended downstream obligations.
