# Incoming-span / runtime-storage-lifetime research candidate

Owner merge. User-authorized internal review publication; not received, integrated,
accepted or upstream-submitted. Previous no-go package 63b54dcd remains unchanged.

VeriFast base f76012fb518703b1d98e243ac4f487f16877cfcb; isolated branch
merge/incoming-span-lifetime-20261009; tool commit
75099c958eb6a6d46016babf0a845a624f77d9ab. Portable patch and prerequisite-limited
bundle are supplied. No broad declaration-heap exclusion from 2f61/8c is active.

Candidate lowers actual MIR StorageLive/StorageDead, defers address-taken local
storage until live, consumes existing storage at death, removes the path-local
address binding and gives any subsequent live event a fresh address. Geometry
compares only surviving exact physical entry Chunk objects, with positive real
fractions and fixed scalar/pointer byte extents. It creates no permissions or owners.

The generic T consumer remains a no-go for this narrow rule: existing modeled
sizeof specialization does not qualify concrete ZST layout. Generic, struct and
array extents are deliberately excluded. Re-enabling them needs a sound runtime
extent bridge, not an additional supplied separation premise. Storage lifecycle
coverage, normal/unwind closure and common-profile admission remain open.

Apply the portable code patch to the exact base with git am, or fetch the supplied
bundle into an isolated review branch with base present. The proof experiment also
applies its pinned tracked-MD patch and historical six-profile patches; use the
published proof commit and PROFILE/build-profile artifacts rather than mixing pins.
Compilation, extraction and verification must run through the authorized Cloud
recipe/coordinator; local work is limited to Git, static reading and service replay.

Detailed controls, rationale, independent review, immutable evidence and exact
results are included below the package root. Tests are not global soundness proof.

Final status: NOT_FOR_INTEGRATION. In addition to the excluded generic extent
domain, spelling-based lifecycle CallExpr markers have an unresolved origin
gate (extern-prototype/diverging source call may forge an event). This is static
review evidence, not an executed exploit. Six mechanism controls match in
cae0f3cc-9ca4-4ceb-b570-ab5e26e6ce82; all five actual cases stop before FBC at
line69 and are INCONCLUSIVE for their intended downstream obligations.
