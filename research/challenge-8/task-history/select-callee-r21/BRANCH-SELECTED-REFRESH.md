# R21 branch-selected final-select certificate refresh

The R20 repair closed the wrappers with their original `true_payload` and
`false_payload` names in both branches. The R20 S3b proof observation showed that
reopening the guard gives the selected wrapper a fresh `selected_payload`;
S2d binds the prepared branch-selected variant to its source/MIR pins.
Using an original payload for that wrapper therefore misses the value bound by
the reopened guard.

The R21 refresh applies only to the nine-body actual `select_unpredictable`
unit at verified source SHA-256
`b9430169d01a2eca19728c38d05da818bdfc4e05561671c33ed95eb5830de45d`. Its
source-only translator patch is
`research/challenge-8/overnight-assume-actual/verifast-r21-final-select-branch-selected-26.10.patch`,
SHA-256 `78079210a5548fee87e200996920bfb012bcb0cd17b0b574eb926806a46e7ab6`.
It pins body 7 to
`60861a6280f06196e3cab9e366ba8d5ade71d58d0aa29a79a90ed73ecc301094` and the
decoded unit to
`b8d367293b9d1ae8af186edeee0817f1b8bfe04250462fe75386fcd288e214eb`. The
baseline original source SHA-256 is
`466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5`.

The invariant is branch-local ownership: the true branch closes the selected
wrapper with `selected_payload` and the unselected wrapper with
`false_payload`; the false branch closes the unselected wrapper with
`true_payload` and the selected wrapper with `selected_payload`. Both closes
remain inside the existing ghost `if` statement, so the patch adds no MIR
branch or runtime operation. The refresh is admitted only through the existing
per-call R20 opt-in together with exact nine-body admission. The default route,
the other eight body pins, and the source and unit gates remain exact; the
three changed certificate identities are the verified source, body 7, and
decoded unit above.

Source-only application of the 20 manifest patches and two refresh patches
produced translator SHA-256
`0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a` before
the R21 patch and
`606235c66c76412d2fdcef5f30436c342771ad5a087b343f618cfb7c8a2344d2` after it.
The R21 patch was checked and applied in a fresh isolated tool worktree at
`f76012fb518703b1d98e243ac4f487f16877cfcb`. The S2d evidence is
Build `79ba86f3-200c-4678-b9b2-80450b0be061`, source-reported: its root
fingerprint is complete, MIR is complete, all ten snapshots are present, and
its location control reproduces the pinned baseline. Bodies 0–6 and 8 retain
their R20 S2c identities.

The runner now applies this patch and uses the existing classified
`r20-repair-proof` mode, which retains the no-opt-in and unrepaired controls.
This refresh records certificate identity only; it establishes no proof
acceptance or independent proof credit. No compiler, exporter, preparer,
verifier, proof runner, or Build was run for this refresh.

## Proof-row source/stage/target binding

Defect: a record with RAN/exit 0 and an unchanged-source flag could be classified without matching the actual verifier argv, source snapshots or row log. Applicability: the newly activated classified proof stage. The main helper now checks the exact verifier executable/arguments/target, expected source-before/source-after and freshly read post-stage file hashes, enabled intrinsic/pointer-drop gates, and row stdout/stderr identity before classification. A mismatch is inconclusive and leaves the matrix incomplete. Original stage dictionaries, exits, exceptions and snapshots remain preserved; no acceptance or independent proof credit is derived.

Controls: test_select_callee_r21.py covers valid source-reported positive/certificate controls, verifier errors, timeout, partial/missing/null/wrong-type/NOT_RUN records, source/argv/target/log/gate mismatches, partial record on an original exception, and flag cleanup. Existing RepairProof fixture now supplies the full stage fields; the classifier does not manufacture missing identity information.
