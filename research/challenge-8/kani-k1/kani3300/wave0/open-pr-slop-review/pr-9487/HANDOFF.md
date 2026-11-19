# READY — PR9487 offline recommendation sealed

Recommendation: CHANGES_RECOMMENDED_DESCRIPTOR_FIX_RETAIN_IMPLEMENTATION_AND_COVERAGE.

P2 F1: `test.desc:4` is `^EXIT=0$`, consumed by `regression/test.pl` as the fourth header/grep-options field. Insert a blank fourth line. The pinned `-e` check sees the EXIT string anywhere but does not make it an evaluated pattern. Seven bounded synthetic parsing/matching cases confirm that the repair rejects a success-marker/nonzero-exit result while preserving real success and signal/invariant/warning/verdict rejection. No driver or native tool was run. The original invariant abort is still rejected by the current test; this finding concerns an incomplete exit oracle.

Keep the one-line production guard change, all three unit cases and the single C regression. Zero-element and zero-width-element arrays have distinct operand shapes; exact typing, tags, nested arrays, nonzero siblings and union selection justify the coverage. No test removals, helper extraction, generated matrix or fixture rewrite is proposed. Optional P3: replace historical descriptor comments and shorten the PR body. Exact edits and a CBMC-template PR suggestion are included.

Read REPORT.md, FINDINGS.json, COVERAGE-EDITS.md, CODE-COMMENT-EDITS.md, SUGGESTED-PR.md, STATIC-CHECK.json, INPUTS.json, PROVENANCE.json and MANIFEST.json.

Task/input commit: `98784e2ade6135d3177b0ad14c9ab88777ab6aa2`.
Published source head: `9f2d01ec2bf115879c86e22203d403ba156d22e5`.
Published tree: `00ef6af1359f247f574bbfab6e6a514442118ba9`.
Connected-confirmed merge base: `107a1e504cd69a2f3483717c8bcfcfa59814c557`.
Connected current upstream base: `57c8ad710ee2f581895478ff4645cebec2f53c49` (not a local object; no direct current-base source-equivalence claim).
Original PR body SHA256: `a43a9b50e632436e654d61407ad20a4f11e9809a65dc4fbb251cce11a7a2bcf2`.
Exact source diff SHA256: `dc94afb14a6611d19a0583b661dd1633f95afdc7c884de69b94898a7bdd152f5`.

All four published blob IDs/SHA256s/bytes, local head/tree/parent and diff match. Source stayed clean/read-only. CBMC LICENSE and actual pull-request template were inspected; Kani Apache/MIT text was not injected. The real Kani#5085 link and AI disclosure remain. Original release/CI claims are author-reported; native tests and CI for any later cleanup revision remain pending. The suggested body is only inside this packet, not a live PR or external owner draft.

No C/C++ compiler, native unit/regression runner, CBMC, CI, push, source edits, external messages/drafts, ledger/accounting, subagent, model or Fast changes. Prior S4P2 intake and independent W13 work remain untouched. This review is complete; root may route the recommendation for separate implementation/review/validation, without automatic execution/publication.

MANIFEST.json seals every other packet file. The full40 containing commit SHA is returned in the final handoff; use that immutable commit rather than a later mutable checkpoint. Verify hashes against its blobs. `static_check.py` replays read-only pins and the bounded descriptor model; it never executes the source's driver or native tools. Review output is confined to `kani3300/wave0/open-pr-slop-review/pr-9487/`.
